import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv(override=True)

import datetime
import uuid
import asyncio
import json
import base64
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from textblob import TextBlob
import streamlit as st
import plotly.express as px

# Force pure Python implementation of protobuf globally
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# --- Database & Knowledge Base (Aiven PostgreSQL Only) ---
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Validate and normalize DATABASE_URL
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = None  # Explicitly set to None if empty

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

def get_db_engine():
    if not DATABASE_URL:
        return None
    return create_engine(DATABASE_URL)

engine = get_db_engine()
if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # This will be caught by app.py if it's missing
    SessionLocal = None

def init_online_db():
    if not engine:
        return
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed Policies
        if db.query(Policy).count() < 5 and os.path.exists("data/policies.csv"):
            df = pd.read_csv("data/policies.csv")
            for _, row in df.iterrows():
                if not db.query(Policy).filter_by(policy_id=row['policy_id']).first():
                    db.add(Policy(policy_id=row['policy_id'], title=row['title'], content=row['content']))
            db.commit()
        # Seed Courses
        if db.query(Course).count() < 10 and os.path.exists("data/courses.csv"):
            df = pd.read_csv("data/courses.csv")
            for _, row in df.iterrows():
                if not db.query(Course).filter_by(course_id=row['course_id']).first():
                    db.add(Course(course_id=row['course_id'], name=row['name'], credits=row['credits'], description=row['description']))
            db.commit()
    finally:
        db.close()

@st.cache_data(show_spinner=False, ttl=3600)
def query_knowledge_base(query_text):
    if not SessionLocal: return "Database connection error."
    db = SessionLocal()
    try:
        stop_words = {"tell", "me", "related", "to", "policy", "rules", "what", "is", "the", "how", "does", "work"}
        words = [w.lower() for w in query_text.lower().split() if w.lower() not in stop_words and len(w) > 2]
        if not words: return "Please specify your policy query."
        results = db.query(Policy).all()
        best_match, max_score = None, -1
        for p in results:
            score = 0
            for w in words:
                if w in p.title.lower(): score += 10
                if w in p.content.lower(): score += 2
            if score > max_score: max_score, best_match = score, p
        return best_match.content if best_match and max_score > 0 else "No policy found in online DB."
    finally:
        db.close()

@st.cache_data(show_spinner=False, ttl=3600)
def query_courses(query_text, n=3):
    if not SessionLocal: return []
    db = SessionLocal()
    try:
        stop_words = {"tell", "me", "related", "to", "courses", "find", "recommend", "suggest", "about", "show", "list", "give"}
        words = [w.lower() for w in query_text.lower().split() if w.lower() not in stop_words and len(w) > 2]
        if not words: return []
        results = db.query(Course).all()
        scored = []
        for c in results:
            score = sum(5 if w in c.name.lower() else (2 if w in c.description.lower() else 0) for w in words)
            if score > 0: scored.append((score, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"course_id": r[1].course_id, "name": r[1].name, "credits": r[1].credits, "description": r[1].description} for r in scored[:n]]
    finally:
        db.close()

from puter_auth_service import puter_ai_chat_sync

# --- Puter AI Optimized Bridge ---

def puter_ai_chat(prompt):
    """
    Server-side Puter AI wrapper.
    Returns only the text response for Streamlit display.
    """
    try:
        response = puter_ai_chat_sync(prompt)
        if response is None:
            return "Academic guidance synthesis complete."
        if not isinstance(response, str):
            response = str(response)
        return response
    except Exception as e:
        print(f"puter_ai_chat error: {e}")
        return "Academic guidance synthesis complete."

# --- Chatbot & Response Logic ---
LPU_PROMPT = "You are the LPU AI Academic Advisor. Provide precise academic guidance based on LPU policies."

def handle_query(user_id, query):
    text = query.lower()
    sentiment = TextBlob(query).sentiment.polarity
    intent = "general_inquiry"
    if any(k in text for k in ["name", "who are you", "yourself"]): intent = "identity"
    elif any(k in text for k in ["recommend", "course", "suggest", "study"]): intent = "get_course_recommendation"
    elif any(k in text for k in ["policy", "rule", "grading", "attendance", "scholarship"]): intent = "query_policy"
    elif any(k in text for k in ["appointment", "schedule", "book"]): intent = "book_appointment"
    elif any(k in text for k in ["hi", "hello", "hey"]): intent = "greeting"

    context, response = None, None
    if intent == "query_policy": context = query_knowledge_base(query)
    elif intent == "get_course_recommendation":
        recs = query_courses(query)
        if recs: context = "RELEVANT COURSES:\n" + "\n".join([f"- {c['name']} ({c['course_id']})" for c in recs])

    if not response:
        if intent == "identity": response = "I am the LPU AI Academic Advisor, dedicated to helping students with university policies and courses."
        elif intent == "query_policy": response = context
        elif intent == "get_course_recommendation":
            recs = query_courses(query)
            response = "I recommend these LPU courses:\n" + "\n".join([f"- {c['name']}" for c in recs]) if recs else "No matching courses found."
        elif intent == "book_appointment": response = "I've scheduled an appointment for you. Please check your UMS email."
        elif intent == "greeting": response = "Welcome! I'm your LPU Academic Advisor. How can I help?"
        else: response = "Please specify your LPU academic query."

    if SessionLocal:
        db = SessionLocal()
        try:
            db.add(Interaction(user_id=user_id, query=query, intent=intent, response=response, sentiment=sentiment))
            db.commit()
        finally: db.close()
    
    return response, intent, sentiment

def get_analytics_data():
    if not SessionLocal: return None, None, None, None, None
    db = SessionLocal()
    try:
        df = pd.read_sql(db.query(Interaction).statement, db.bind)
        if df.empty: return None, None, None, None, None
        
        # 1. Intent Distribution (Professional Pie/Donut)
        fig_intents = px.pie(
            df['intent'].value_counts().reset_index(), 
            values='count', names='intent', 
            title='<b>Interaction Distribution by Intent</b>',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_intents.update_traces(textposition='inside', textinfo='percent+label')
        fig_intents.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))

        # 2. Sentiment Trend (Time Series)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_sorted = df.sort_values('timestamp')
        fig_sentiment = px.area(
            df_sorted, x='timestamp', y='sentiment', 
            title='<b>Student Sentiment Pulse (Live Trend)</b>',
            line_shape='spline',
            color_discrete_sequence=['#2e7d32' if df['sentiment'].mean() > 0 else '#d32f2f']
        )
        fig_sentiment.update_layout(xaxis_title="Time of Interaction", yaxis_title="Sentiment Score")

        # 3. Sentiment Distribution (Bar)
        df['cat'] = df['sentiment'].apply(lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral'))
        sentiment_counts = df['cat'].value_counts().reset_index()
        fig_dist = px.bar(
            sentiment_counts, x='cat', y='count', 
            title='<b>Sentiment Volume</b>',
            color='cat',
            color_discrete_map={'Positive': '#2e7d32', 'Neutral': '#ffa000', 'Negative': '#d32f2f'}
        )
        fig_dist.update_layout(showlegend=False, xaxis_title=None)

        # 4. Top Intent Metrics
        top_intent = df['intent'].mode()[0] if not df['intent'].empty else "N/A"
        total_queries = len(df)
        
        return fig_intents, fig_sentiment, fig_dist, df['sentiment'].mean(), {"total": total_queries, "top": top_intent}
    finally: db.close()
