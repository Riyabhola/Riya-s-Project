import pandas as pd
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy 2.0+ requires 'postgresql://' instead of 'postgres://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- SQLAlchemy Setup ---
engine = None
SessionLocal = None
Base = declarative_base()

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(String(255))
    query = Column(Text)
    intent = Column(String(100))
    response = Column(Text)
    sentiment = Column(Float)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(255))
    advisor_id = Column(String(255))
    date_time = Column(String(100))
    status = Column(String(50), default="Scheduled")

class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    policy_id = Column(String(100), unique=True)
    title = Column(String(255))
    content = Column(Text)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(String(100), unique=True)
    name = Column(String(255))
    credits = Column(Integer)
    description = Column(Text)

def create_db_engine():
    """
    Creates an engine exclusively for Aiven PostgreSQL.
    No local storage is permitted.
    """
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL environment variable is missing. Online database required.")
        return None
    try:
        tmp_engine = create_engine(DATABASE_URL)
        # Verify connectivity immediately
        with tmp_engine.connect() as conn:
            print("Successfully connected to Aiven PostgreSQL.")
        return tmp_engine
    except Exception as e:
        print(f"ERROR: Failed to connect to Aiven PostgreSQL: {e}")
        return None

# Initialize engine
engine = create_db_engine()
if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    raise RuntimeError("Aiven PostgreSQL connection is mandatory.")

def init_online_db():
    """Initializes the relational database schema and seeds data from CSVs if empty."""
    if not engine:
        return
    try:
        Base.metadata.create_all(bind=engine)
        print("Online database schema initialized.")
        
        db = SessionLocal()
        try:
            # Seed Policies
            if db.query(Policy).count() == 0:
                if os.path.exists("data/policies.csv"):
                    print("Seeding policies to Aiven PostgreSQL...")
                    df = pd.read_csv("data/policies.csv")
                    for _, row in df.iterrows():
                        policy = Policy(policy_id=row['policy_id'], title=row['title'], content=row['content'])
                        db.add(policy)
                    db.commit()

            # Seed Courses
            if db.query(Course).count() == 0:
                if os.path.exists("data/courses.csv"):
                    print("Seeding courses to Aiven PostgreSQL...")
                    df = pd.read_csv("data/courses.csv")
                    for _, row in df.iterrows():
                        course = Course(course_id=row['course_id'], name=row['name'], credits=row['credits'], description=row['description'])
                        db.add(course)
                    db.commit()
        finally:
            db.close()
            
    except Exception as e:
        print(f"Critical Error: Could not initialize/seed database: {e}")

def log_interaction(user_id, query, intent, response, sentiment):
    db = SessionLocal()
    try:
        new_interaction = Interaction(
            user_id=user_id, query=query, intent=intent, response=response, sentiment=sentiment
        )
        db.add(new_interaction)
        db.commit()
    finally:
        db.close()

def get_interactions():
    db = SessionLocal()
    try:
        query = db.query(Interaction)
        return pd.read_sql(query.statement, db.bind)
    finally:
        db.close()

def get_recent_interactions(user_id, limit=5):
    db = SessionLocal()
    try:
        interactions = db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).order_by(Interaction.timestamp.desc()).limit(limit).all()
        return interactions[::-1]
    finally:
        db.close()

def book_appointment(student_id, advisor_id, date_time):
    db = SessionLocal()
    try:
        new_appointment = Appointment(student_id=student_id, advisor_id=advisor_id, date_time=date_time)
        db.add(new_appointment)
        db.commit()
    finally:
        db.close()

def query_courses(query_text, n_results=3):
    """Searches courses in Aiven PostgreSQL using basic keyword matching."""
    db = SessionLocal()
    try:
        # Professional keyword-based search on Aiven
        words = query_text.lower().split()
        results = db.query(Course).all()
        scored_results = []
        for c in results:
            score = sum(1 for w in words if w in c.name.lower() or w in c.description.lower())
            if score > 0:
                scored_results.append((score, c))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        top_recs = [r[1] for r in scored_results[:n_results]]
        
        return [{"course_id": c.course_id, "name": c.name, "credits": c.credits, "description": c.description} for c in top_recs]
    finally:
        db.close()

def query_knowledge_base(query_text, n_results=1):
    """Searches policies in Aiven PostgreSQL using basic keyword matching."""
    db = SessionLocal()
    try:
        words = query_text.lower().split()
        results = db.query(Policy).all()
        best_match = None
        max_score = -1
        
        for p in results:
            score = sum(2 for w in words if w in p.title.lower()) + sum(1 for w in words if w in p.content.lower())
            if score > max_score:
                max_score = score
                best_match = p
        
        return best_match.content if best_match and max_score > 0 else "I'm sorry, I couldn't find any specific LPU policy regarding that in our online database."
    finally:
        db.close()

if __name__ == "__main__":
    init_online_db()
    print("Aiven PostgreSQL Knowledge Base initialized.")
