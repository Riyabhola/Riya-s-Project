import os
from textblob import TextBlob
from logic.database import query_knowledge_base, log_interaction, book_appointment, query_courses
import pandas as pd
import random
import google.generativeai as genai

# --- Gemini Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

LPU_ADVISOR_SYSTEM_PROMPT = """
You are the "LPU AI Academic Advisor", a professional, supportive, and highly accurate assistant for students at Lovely Professional University (LPU).
Your goal is to provide precise academic guidance based ONLY on the provided context and LPU's official policies.

Core Guidelines:
1. Tone: Professional yet empathetic and encouraging.
2. Accuracy: Strictly follow LPU policies (e.g., 75% attendance rule, CGPA requirements).
3. Clarity: Use bullet points for complex information.
4. Scope: If the user asks something outside the provided context or general LPU knowledge, politely redirect them to the LPU UMS portal or a faculty advisor.
5. Identity: Always identify as the LPU AI Academic Advisor.

Context will be provided for specific queries. If no context is provided, use your internal knowledge of being a supportive advisor to guide the student.
"""

def generate_response_with_llm(query, context, intent):
    """
    Generates a synthesized response using Gemini based on context.
    """
    if not model:
        return None # Fallback to original logic

    prompt = f"{LPU_ADVISOR_SYSTEM_PROMPT}\n\n"
    if context:
        prompt += f"CONTEXT FROM LPU DATABASE:\n{context}\n\n"
    
    prompt += f"USER QUERY: {query}\n"
    prompt += "ADVISOR RESPONSE:"

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        return None

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
    if any(k in text for k in ["your interest", "who are you", "what do you do", "about yourself", "how are you", "who is your creator"]):
        return "small_talk", {}
        
    # 2. Course Recommendations
    if any(k in text for k in ["recommend", "course", "suggest", "take classes", "which subject", "learn about", "study"]):
        return "get_course_recommendation", {}
    
    if "interest" in text and "your" not in text:
        return "get_course_recommendation", {}

    # 3. Policy Queries (Expanded)
    elif any(k in text for k in ["policy", "rule", "requirement", "grading", "scale", "probation", "credit", "hours", "graduate", "attendance", "scholarship", "ums", "placement", "exam", "test", "backlog", "re-appear"]):
        return "query_policy", {}
    
    # 4. Appointments
    elif any(k in text for k in ["appointment", "schedule", "book", "meeting", "advisor", "see someone", "talk to faculty"]):
        return "book_appointment", {"date": "tomorrow at 10am"}
    
    # 5. Greetings
    elif any(k in text for k in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon"]):
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
    
    context = None
    response = None

    # 3. Fetch Context based on Intent
    if intent == "query_policy":
        context = query_knowledge_base(query_text)
    elif intent == "get_course_recommendation":
        recs = query_courses(query_text)
        if recs:
            context = "\n".join([f"Course: {c['name']}, ID: {c['course_id']}, Credits: {c['credits']}, Description: {c['description']}" for c in recs])
    
    # 4. Generate Response with LLM (if available)
    if GEMINI_API_KEY:
        response = generate_response_with_llm(query_text, context, intent)
    
    # 5. Fallback Logic (if LLM is unavailable or fails)
    if not response:
        if intent == "small_talk":
            response = "As an AI Academic Advisor for LPU, my interests lie in helping you succeed! I'm passionate about university policies, course planning, and making your academic journey at Lovely Professional University smoother."
        elif intent == "query_policy":
            response = context if context else "I'm sorry, I couldn't find any specific LPU policy regarding that."
        elif intent == "get_course_recommendation":
            response = get_course_recommendations(query_text)
        elif intent == "book_appointment":
            date_time = parameters.get("date", "Next available slot")
            book_appointment(user_id, "LPU Faculty Advisor", date_time)
            response = f"I've scheduled an appointment for you with an LPU Faculty Advisor on {date_time}. Please check your LPU UMS email for the confirmation link."
        elif intent == "greeting":
            response = "Hello! I'm your LPU AI Academic Advisor. How can I assist you with your LPU academic planning or university policy queries today?"
        else:
            response = "I am your LPU academic advisor. You can ask me about university-specific course recommendations, LPU academic policies (like attendance or grading), or schedule an appointment with a faculty advisor."

    # 6. Log Interaction (Handle DB failures gracefully)
    try:
        log_interaction(user_id, query_text, intent, response, sentiment)
    except Exception as e:
        print(f"Failed to log interaction: {e}")
    
    return response, intent, sentiment
