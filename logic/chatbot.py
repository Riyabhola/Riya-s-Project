import os
from textblob import TextBlob
from logic.database import query_knowledge_base, log_interaction, book_appointment
import pandas as pd
import random

# Mock Dialogflow logic
def detect_intent_mock(text):
    text = text.lower()
    if any(k in text for k in ["recommend", "course", "suggest", "take", "classes"]):
        return "get_course_recommendation", {}
    elif any(k in text for k in ["policy", "rule", "requirement", "grading", "scale", "probation", "credit", "hours", "graduate"]):
        return "query_policy", {}
    elif any(k in text for k in ["appointment", "schedule", "book", "meeting", "advisor", "see someone"]):
        return "book_appointment", {"date": "tomorrow at 10am"}
    elif any(k in text for k in ["hi", "hello", "hey", "greetings"]):
        return "greeting", {}
    else:
        return "general_inquiry", {}

def get_course_recommendations(query_text=""):
    courses_df = pd.read_csv("data/courses.csv")
    query_text = query_text.lower()
    
    # Try to identify department from query
    departments = courses_df['department'].unique()
    target_dept = None
    for dept in departments:
        if dept.lower() in query_text:
            target_dept = dept
            break
            
    # Try to identify level from query
    levels = courses_df['level'].unique()
    target_level = None
    for lvl in levels:
        if lvl.lower() in query_text:
            target_level = lvl
            break

    recommendations = courses_df
    if target_dept:
        recommendations = recommendations[recommendations['department'] == target_dept]
    if target_level:
        recommendations = recommendations[recommendations['level'] == target_level]
    
    if recommendations.empty or (not target_dept and not target_level):
        recommendations = courses_df.sample(min(3, len(courses_df)))
    else:
        recommendations = recommendations.head(3)
        
    response = "Based on your interest, I recommend the following courses:\n"
    for _, row in recommendations.iterrows():
        response += f"- {row['course_id']}: {row['name']} ({row['credits']} credits) - {row['description']}\n"
    return response

def handle_query(user_id, query_text):
    # 1. Detect Intent
    intent, parameters = detect_intent_mock(query_text)
    
    # 2. Analyze Sentiment
    sentiment = TextBlob(query_text).sentiment.polarity
    
    # 3. Generate Response based on Intent
    if intent == "query_policy":
        response = query_knowledge_base(query_text)
    elif intent == "get_course_recommendation":
        response = get_course_recommendations(query_text)
    elif intent == "book_appointment":
        # Simulate booking
        date_time = parameters.get("date", "Next available slot")
        book_appointment(user_id, "Advisor Smith", date_time)
        response = f"I've scheduled an appointment for you with Advisor Smith on {date_time}. You will receive a confirmation email shortly."
    elif intent == "greeting":
        response = "Hello! I'm your AI Academic Advisor. How can I assist you with your academic planning today?"
    else:
        response = "I'm your academic advisor. You can ask me about course recommendations, university policies, or schedule an appointment. For example, try 'What is the grading scale?' or 'Recommend some CS courses'."

    # 4. Log Interaction
    log_interaction(user_id, query_text, intent, response, sentiment)
    
    return response, intent, sentiment
