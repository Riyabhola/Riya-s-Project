import sqlite3
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os

DB_PATH = "data/student_interactions.db"
CHROMA_PATH = "data/chroma_db"

def init_sqlite():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Interaction logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            query TEXT,
            intent TEXT,
            response TEXT,
            sentiment REAL
        )
    ''')
    
    # Appointments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            advisor_id TEXT,
            date_time TEXT,
            status TEXT DEFAULT 'Scheduled'
        )
    ''')
    
    conn.commit()
    conn.close()

def log_interaction(user_id, query, intent, response, sentiment):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interactions (user_id, query, intent, response, sentiment)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, query, intent, response, sentiment))
    conn.commit()
    conn.close()

def get_interactions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interactions", conn)
    conn.close()
    return df

def book_appointment(student_id, advisor_id, date_time):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (student_id, advisor_id, date_time)
        VALUES (?, ?, ?)
    ''', (student_id, advisor_id, date_time))
    conn.commit()
    conn.close()

def init_chroma():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # Using default embedding function (sentence-transformers)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # 1. Policies Collection
    policy_collection = client.get_or_create_collection(name="policies", embedding_function=emb_fn)
    if policy_collection.count() == 0:
        policies_df = pd.read_csv("data/policies.csv")
        policy_collection.add(
            documents=policies_df['content'].tolist(),
            metadatas=[{"title": t} for t in policies_df['title'].tolist()],
            ids=policies_df['policy_id'].tolist()
        )
    
    # 2. Courses Collection for Semantic Recommendation
    course_collection = client.get_or_create_collection(name="courses", embedding_function=emb_fn)
    if course_collection.count() == 0:
        courses_df = pd.read_csv("data/courses.csv")
        # Combine name and description for better semantic matching
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
    return results['documents'][0][0] if results['documents'] else "I'm sorry, I couldn't find any specific policy regarding that."

if __name__ == "__main__":
    init_sqlite()
    init_chroma()
    print("Databases initialized.")
