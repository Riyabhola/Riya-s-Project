import os
from textblob import TextBlob
from logic.database import query_knowledge_base, log_interaction, book_appointment, query_courses
import pandas as pd
import random

# Dialogflow Configuration (Placeholder for production)
# from google.cloud import dialogflow_v2 as dialogflow
# DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")
# DIALOGFLOW_SESSION_ID = "current-session"

def detect_intent(text, user_id):
    """
    Detects intent using Dialogflow if configured, otherwise falls back to mock.
    """
    if os.getenv("DIALOGFLOW_PROJECT_ID"):
        # Real Dialogflow integration would go here
        # return detect_intent_dialogflow(text, user_id)
        pass
    return detect_intent_mock(text)

# Mock Dialogflow logic
def detect_intent_mock(text):
    text = text.lower()
    
    # 1. Bot Personality / Small Talk (Priority)
    if any(k in text for k in ["your interest", "who are you", "what do you do", "about yourself", "how are you"]):
        return "small_talk", {}
        
    # 2. Course Recommendations (Refined keywords to avoid collision with 'interest')
    if any(k in text for k in ["recommend", "course", "suggest", "take classes", "which subject", "learn about"]):
        return "get_course_recommendation", {}
    
    # Check for 'interest' only if not already handled by small talk
    if "interest" in text and "your" not in text:
        return "get_course_recommendation", {}

    elif any(k in text for k in ["policy", "rule", "requirement", "grading", "scale", "probation", "credit", "hours", "graduate", "attendance", "scholarship", "ums", "placement"]):
        return "query_policy", {}
    elif any(k in text for k in ["appointment", "schedule", "book", "meeting", "advisor", "see someone"]):
        return "book_appointment", {"date": "tomorrow at 10am"}
    elif any(k in text for k in ["hi", "hello", "hey", "greetings"]):
        return "greeting", {}
    else:
        return "general_inquiry", {}

def get_course_recommendations(query_text=""):
    """
    Uses semantic search (ChromaDB) to find relevant LPU courses.
    """
    recommendations = query_courses(query_text)
    
    if not recommendations:
        return "I'm sorry, I couldn't find any LPU courses matching your interests at the moment."
        
    response = "Based on your interest, I recommend the following courses at Lovely Professional University:\n"
    for course in recommendations:
        response += f"- **{course['course_id']}**: {course['name']} ({course['credits']} credits)  \n  *{course['description']}*\n"
    return response

def handle_query(user_id, query_text):
    # 1. Detect Intent
    intent, parameters = detect_intent(query_text, user_id)
    
    # 2. Analyze Sentiment
    sentiment = TextBlob(query_text).sentiment.polarity
    
    # 3. Generate Response based on Intent
    if intent == "small_talk":
        response = "As an AI Academic Advisor for LPU, my interests lie in helping you succeed! I'm passionate about university policies, course planning, and making your academic journey at Lovely Professional University smoother."
    elif intent == "query_policy":
        response = query_knowledge_base(query_text)
    elif intent == "get_course_recommendation":
        response = get_course_recommendations(query_text)
    elif intent == "book_appointment":
        # Simulate booking
        date_time = parameters.get("date", "Next available slot")
        book_appointment(user_id, "LPU Faculty Advisor", date_time)
        response = f"I've scheduled an appointment for you with an LPU Faculty Advisor on {date_time}. Please check your LPU UMS email for the confirmation link."
    elif intent == "greeting":
        response = "Hello! I'm your LPU AI Academic Advisor. How can I assist you with your LPU academic planning or university policy queries today?"
    else:
        response = "I am your LPU academic advisor. You can ask me about university-specific course recommendations, LPU academic policies (like attendance or grading), or schedule an appointment with a faculty advisor."

    # 4. Log Interaction
    log_interaction(user_id, query_text, intent, response, sentiment)
    
    return response, intent, sentiment
