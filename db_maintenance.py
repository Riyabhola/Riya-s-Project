import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import advisor_logic

load_dotenv(override=True)

def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url: raise ValueError("DATABASE_URL not found")
    if url.startswith("postgres://"): url = url.replace("postgres://", "postgresql://", 1)
    return create_engine(url)

def backup_interactions():
    """Backup interaction logs to a local CSV file."""
    print("🚀 Starting Professional Backup: 'interactions' table...")
    engine = get_engine()
    try:
        df = pd.read_sql("SELECT * FROM interactions", engine)
        filename = f"data/interactions_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Backup successful: {filename} ({len(df)} records)")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def force_reseed():
    """Clears and re-seeds the policies and courses tables."""
    print("🚀 Starting Professional Re-seed...")
    engine = get_engine()
    advisor_logic.Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing
        db.execute(text("TRUNCATE TABLE policies, courses RESTART IDENTITY CASCADE"))
        print("✅ Tables truncated.")
        
        # Seed Policies
        if os.path.exists("data/policies.csv"):
            df = pd.read_csv("data/policies.csv")
            for _, row in df.iterrows():
                db.add(advisor_logic.Policy(policy_id=row['policy_id'], title=row['title'], content=row['content']))
            print(f"✅ Seeded {len(df)} policies.")
            
        # Seed Courses
        if os.path.exists("data/courses.csv"):
            df = pd.read_csv("data/courses.csv")
            for _, row in df.iterrows():
                db.add(advisor_logic.Course(course_id=row['course_id'], name=row['name'], credits=row['credits'], description=row['description']))
            print(f"✅ Seeded {len(df)} courses.")
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Re-seed failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "backup": backup_interactions()
        elif sys.argv[1] == "reseed": force_reseed()
        else: print("Usage: python db_maintenance.py [backup|reseed]")
    else:
        print("Professional Database Maintenance Tool")
        print("Available commands: backup, reseed")
