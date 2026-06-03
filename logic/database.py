import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/student_interactions.db")
# SQLAlchemy 2.0+ requires 'postgresql://' instead of 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

CHROMA_PATH = "data/chroma_db"

# --- SQLAlchemy Setup ---
def create_db_engine():
    db_url = os.getenv("DATABASE_URL", "sqlite:///data/student_interactions.db")
    # SQLAlchemy 2.0+ requires 'postgresql://' instead of 'postgres://'
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    try:
        temp_engine = create_engine(db_url)
        # Try to connect to verify the URL/credentials are valid
        with temp_engine.connect() as conn:
            pass
        return temp_engine
    except Exception as e:
        print(f"Warning: Primary database connection failed ({e}). Falling back to local SQLite.")
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        return create_engine("sqlite:///data/student_interactions.db")

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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

def init_sqlite():
    """Initializes the relational database schema."""
    try:
        Base.metadata.create_all(bind=engine)
        print(f"Database initialized successfully using: {engine.url}")
    except Exception as e:
        print(f"Critical Error: Could not initialize database schema: {e}")

def log_interaction(user_id, query, intent, response, sentiment):
    db = SessionLocal()
    try:
        new_interaction = Interaction(
            user_id=user_id,
            query=query,
            intent=intent,
            response=response,
            sentiment=sentiment
        )
        db.add(new_interaction)
        db.commit()
    finally:
        db.close()

def get_interactions():
    db = SessionLocal()
    try:
        # Load into DataFrame for analytics compatibility
        query = db.query(Interaction)
        df = pd.read_sql(query.statement, db.bind)
        return df
    finally:
        db.close()

def book_appointment(student_id, advisor_id, date_time):
    db = SessionLocal()
    try:
        new_appointment = Appointment(
            student_id=student_id,
            advisor_id=advisor_id,
            date_time=date_time
        )
        db.add(new_appointment)
        db.commit()
    finally:
        db.close()

# --- ChromaDB (Vector Knowledge Base) ---
def init_chroma():
    """Initializes ChromaDB from CSV files if not already present."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # 1. Policies Collection
    policy_collection = client.get_or_create_collection(name="policies", embedding_function=emb_fn)
    if policy_collection.count() == 0:
        if os.path.exists("data/policies.csv"):
            policies_df = pd.read_csv("data/policies.csv")
            policy_collection.add(
                documents=policies_df['content'].tolist(),
                metadatas=[{"title": t} for t in policies_df['title'].tolist()],
                ids=policies_df['policy_id'].tolist()
            )
    
    # 2. Courses Collection
    course_collection = client.get_or_create_collection(name="courses", embedding_function=emb_fn)
    if course_collection.count() == 0:
        if os.path.exists("data/courses.csv"):
            courses_df = pd.read_csv("data/courses.csv")
            course_docs = (courses_df['name'] + ": " + courses_df['description']).tolist()
            course_ids = courses_df['course_id'].tolist()
            course_metadatas = courses_df.to_dict('records')
            
            course_collection.add(
                documents=course_docs,
                metadatas=course_metadatas,
                ids=course_ids
            )
    
    return policy_collection, course_collection

def query_courses(query_text, n_results=3):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_collection(name="courses", embedding_function=emb_fn)
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results['metadatas'][0] if results['metadatas'] else []

def query_knowledge_base(query_text, n_results=1):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_collection(name="policies", embedding_function=emb_fn)
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results['documents'][0][0] if results['documents'] else "I'm sorry, I couldn't find any specific LPU policy regarding that."

if __name__ == "__main__":
    init_sqlite()
    init_chroma()
    print("Databases initialized with SQLAlchemy abstraction.")
