import os
from textblob import TextBlob
from logic.database import query_knowledge_base, log_interaction, book_appointment, query_courses, get_recent_interactions
import pandas as pd
import random
import google.generativeai as genai
import asyncio
from putergenai import PuterClient

# --- Gemini Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- Puter Configuration (Automated Anonymous Access) ---
# No credentials required for Puter's seamless guest AI mode.

LPU_ADVISOR_SYSTEM_PROMPT = """
You are the "LPU AI Academic Advisor", a professional, supportive, and highly accurate assistant for students at Lovely Professional University (LPU).
Your goal is to provide precise academic guidance based ONLY on the provided context and LPU's official policies.

Core Guidelines:
1. Tone: Professional yet empathetic and encouraging.
2. Accuracy: Strictly follow LPU policies (e.g., 75% attendance rule, CGPA requirements).
3. Clarity: Use bullet points for complex information.
4. Scope: If the user asks something outside the provided context or general LPU knowledge, politely redirect them to the LPU UMS portal or a faculty advisor.
5. Identity: Always identify as the LPU AI Academic Advisor.

Context will be provided for specific queries. You must also consider the CONVERSATION HISTORY to maintain continuity and answer follow-up questions accurately.
"""

async def _call_puter_ai_automated(query, context, history=""):
    """
    DEPRECATED in favor of frontend Puter.js Bridge for true anonymous access.
    Kept as an optional backend hook if PUTER_TOKEN is provided.
    """
    puter_token = os.getenv("PUTER_TOKEN")
    if not puter_token:
        return None # Gracefully skip backend Puter call if no token
        
    try:
        async with PuterClient(token=puter_token) as client:
            prompt = f"{LPU_ADVISOR_SYSTEM_PROMPT}\n\n"
            if history:
                prompt += f"CONVERSATION HISTORY:\n{history}\n\n"
            if context:
                prompt += f"KNOWLEDGE CONTEXT:\n{context}\n\n"
            prompt += f"USER QUERY: {query}\nADVISOR RESPONSE:"
            
            result = await client.ai_chat(prompt, options={"model": "gpt-4o"})
            if "response" in result and "result" in result["response"]:
                return result["response"]["result"]["message"]["content"].strip()
            return None
    except Exception as e:
        # Suppress authentication errors in production
        return None

def generate_response_with_llm(query, context, intent, history=""):
    """
    Generates a synthesized response using Gemini or Backend Puter (if token available).
    The main 'Seamless' bypass is now handled via the Puter.js Bridge in app.py.
    """
    # 1. Primary Backend: Gemini (If key is manually provided)
    if model:
        prompt = f"{LPU_ADVISOR_SYSTEM_PROMPT}\n\n"
        if history:
            prompt += f"CONVERSATION HISTORY:\n{history}\n\n"
        if context:
            prompt += f"KNOWLEDGE CONTEXT:\n{context}\n\n"
        prompt += f"USER QUERY: {query}\nADVISOR RESPONSE:"
        try:
            gemini_response = model.generate_content(prompt)
            return gemini_response.text.strip()
        except Exception as e:
            pass

    # 2. Secondary Backend: Puter (Only if PUTER_TOKEN is present)
    if os.getenv("PUTER_TOKEN"):
        try:
            return asyncio.run(_call_puter_ai_automated(query, context, history))
        except Exception as e:
            pass

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
    elif any(k in text for k in ["policy", "rule", "requirement", "grading", "scale", "probation", "credit", "hours", "graduate", "attendance", "scholarship", "ums", "placement", "exam", "test", "backlog", "re-appear", "fee", "cost", "mca", "btech", "admission"]):
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
    
    # 3. Retrieve Conversation History
    recent_interactions = get_recent_interactions(user_id, limit=3)
    history_context = ""
    for interaction in recent_interactions:
        history_context += f"User: {interaction.query}\nAdvisor: {interaction.response}\n"
    
    context = None
    response = None

    # 4. Fetch Knowledge Context based on Intent
    if intent == "query_policy":
        context = query_knowledge_base(query_text)
    elif intent == "get_course_recommendation":
        recs = query_courses(query_text)
        if recs:
            context = "\n".join([f"Course: {c['name']}, ID: {c['course_id']}, Credits: {c['credits']}, Description: {c['description']}" for c in recs])
    
    # 5. Generate Response with LLM (passing history)
    response = generate_response_with_llm(query_text, context, intent, history_context)
    
    # 6. Fallback Logic (if LLM is unavailable or fails)
    if not response:
        if intent == "small_talk":
            response = "As an AI Academic Advisor for LPU, my interests lie in helping you succeed! I'm passionate about university policies, course planning, and making your academic journey at Lovely Professional University smoother."
        elif intent == "query_policy":
            if context and "I'm sorry, I couldn't find" not in context:
                response = context
            else:
                response = "SEARCH_FAILURE: Could not find specific LPU policy details."
        elif intent == "get_course_recommendation":
            response = get_course_recommendations(query_text)
        elif intent == "book_appointment":
            date_time = parameters.get("date", "Next available slot")
            book_appointment(user_id, "LPU Faculty Advisor", date_time)
            response = f"I've scheduled an appointment for you with an LPU Faculty Advisor on {date_time}. Please check your LPU UMS email for the confirmation link."
        elif intent == "greeting":
            response = "Hello! I'm your LPU AI Academic Advisor. How can I assist you today?"
        else:
            response = "GENERAL_QUERY_FALLBACK: Please specify your LPU academic inquiry."

    # 7. Log Interaction (Handle DB failures gracefully)
    try:
        log_interaction(user_id, query_text, intent, response, sentiment)
    except Exception as e:
        print(f"Failed to log interaction: {e}")
    
    return response, intent, sentiment
