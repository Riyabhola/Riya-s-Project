import os
from textblob import TextBlob
from logic.database import query_knowledge_base, log_interaction, book_appointment, query_courses, get_recent_interactions
import asyncio
from putergenai import PuterClient

# --- Puter Configuration (Automated Anonymous Access) ---
# No credentials required for Puter's seamless guest AI mode.

LPU_ADVISOR_SYSTEM_PROMPT = """
You are the "LPU AI Academic Advisor", a professional, supportive, and highly accurate assistant for students at Lovely Professional University (LPU).
Your goal is to provide precise academic guidance based ONLY on the provided context and LPU's official policies.

Core Guidelines:
1. Tone: Professional, authoritative, and helpful.
2. Accuracy: Strictly follow LPU policies (e.g., 75% attendance rule, CGPA requirements).
3. Clarity: Use structured bullet points and bold text for key terms.
4. Scope: If the user asks something outside the provided context, inform them that you are limited to academic advising for LPU and suggest contacting the university directly or checking the UMS portal.
5. Identity: Never break character. You are a dedicated LPU academic resource.

Context will be provided for specific queries. You must prioritize the KNOWLEDGE CONTEXT above all else.
"""

async def _call_puter_ai_automated(query, context, history=""):
    """
    Calls Puter AI. Uses PUTER_TOKEN if available.
    """
    puter_token = os.getenv("PUTER_TOKEN")
    if not puter_token:
        return None
    
    try:
        client = PuterClient(token=puter_token)
        async with client as c:
            # Crafting a more precise prompt for the LLM
            prompt = f"SYSTEM INSTRUCTION: {LPU_ADVISOR_SYSTEM_PROMPT}\n\n"
            if history:
                prompt += f"CONVERSATION HISTORY (for context only):\n{history}\n\n"
            if context:
                prompt += f"OFFICIAL LPU KNOWLEDGE CONTEXT (PRIORITY):\n{context}\n\n"
            prompt += f"STUDENT QUERY: {query}\n\nLPU ADVISOR RESPONSE:"
            
            result = await c.ai_chat(prompt, options={"model": "gpt-4o-mini"})
            
            if isinstance(result, dict) and "response" in result:
                res_obj = result["response"]
                if "result" in res_obj and "message" in res_obj["result"]:
                    return res_obj["result"]["message"]["content"].strip()
            elif isinstance(result, str):
                return result
            
            return None
    except Exception as e:
        print(f"Puter Backend SDK Error: {e}")
        return None

def generate_response_with_llm(query, context, intent, history=""):
    """
    Generates a synthesized response exclusively using Puter AI.
    """
    try:
        puter_response = asyncio.run(_call_puter_ai_automated(query, context, history))
        if puter_response:
            return puter_response
    except Exception as e:
        print(f"Puter Execution Error: {e}")

    return None

# Intent Detection Engine
def detect_intent(text):
    """
    Detects LPU-specific intents with high precision keywords.
    """
    text = text.lower()
    
    # 1. Identity / Small Talk
    if any(k in text for k in ["your name", "who are you", "what are you", "yourself", "how are you", "your creator"]):
        return "identity", {}
        
    # 2. Course Recommendations
    if any(k in text for k in ["recommend", "course", "suggest", "take classes", "which subject", "study fashion", "cse courses", "related to"]):
        return "get_course_recommendation", {}

    # 3. Policy Queries
    if any(k in text for k in ["policy", "rule", "requirement", "grading", "scale", "probation", "credit", "attendance", "scholarship", "fee", "admission"]):
        return "query_policy", {}
    
    # 4. Appointments
    if any(k in text for k in ["appointment", "schedule", "book", "meeting", "advisor", "see faculty"]):
        return "book_appointment", {"date": "tomorrow at 10am"}
    
    # 5. Greetings
    if any(k in text for k in ["hi", "hello", "hey", "greetings"]):
        return "greeting", {}
    
    return "general_inquiry", {}

def get_course_recommendations(query_text=""):
    """
    Uses semantic search (Aiven) to find relevant LPU courses.
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
    intent, parameters = detect_intent(query_text)
    
    # 2. Analyze Sentiment
    sentiment = TextBlob(query_text).sentiment.polarity
    
    # 3. Retrieve Conversation History
    recent_interactions = get_recent_interactions(user_id, limit=3)
    history_context = ""
    for interaction in recent_interactions:
        history_context += f"Student: {interaction.query}\nAdvisor: {interaction.response}\n"
    
    context = None
    response = None

    # 4. Fetch Knowledge Context based on Intent
    if intent == "query_policy":
        context = query_knowledge_base(query_text)
    elif intent == "get_course_recommendation":
        recs = query_courses(query_text)
        if recs:
            context = "RELEVANT LPU COURSES:\n" + "\n".join([f"- {c['course_id']}: {c['name']} ({c['credits']} credits). {c['description']}" for c in recs])
    
    # 5. Generate Response with LLM
    response = generate_response_with_llm(query_text, context, intent, history_context)
    
    # 6. Fallback Logic (Precision fallback)
    if not response:
        if intent == "identity":
            response = "I am the LPU AI Academic Advisor, a specialized assistant designed to help students of Lovely Professional University navigate their academic journey, understand university policies, and discover relevant courses."
        elif intent == "query_policy":
            response = context if context else "I'm sorry, I couldn't find a specific LPU policy regarding your query in our online database. Please check the LPU UMS portal for the most up-to-date information."
        elif intent == "get_course_recommendation":
            response = get_course_recommendations(query_text)
        elif intent == "book_appointment":
            date_time = parameters.get("date", "Next available slot")
            book_appointment(user_id, "LPU Faculty Advisor", date_time)
            response = f"I've scheduled an appointment for you with an LPU Faculty Advisor for {date_time}. Please check your UMS registered email for confirmation."
        elif intent == "greeting":
            response = "Welcome! I'm your LPU Academic Advisor. How can I help you with your university journey today?"
        else:
            response = "I'm here to assist with LPU academic matters. Could you please specify your query regarding LPU courses, policies, or advisor appointments?"

    # 7. Log Interaction (Handle DB failures gracefully)
    try:
        log_interaction(user_id, query_text, intent, response, sentiment)
    except Exception as e:
        print(f"Failed to log interaction: {e}")
    
    return response, intent, sentiment
