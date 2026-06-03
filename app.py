import os
# Force pure Python implementation of protobuf for Python 3.14 compatibility
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import streamlit as st
import logging
import warnings

# Suppress verbose logs and warnings
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="Accessing .* from .* Returning .* instead.")

from logic.chatbot import handle_query
from logic.analytics import get_analytics_data
from logic.database import init_online_db
from logic.puter_bridge import puter_ai_chat
import uuid

# Initialize online database on startup
init_online_db()

st.set_page_config(page_title="LPU Academic Advisor", layout="wide")

# Session State for Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

def main():
    st.sidebar.title("🦁 LPU Advisor Hub")
    st.sidebar.info("This AI-powered assistant is dedicated to students of Lovely Professional University (LPU). It uses Puter.js to provide seamless, keyless academic guidance.")
    
    page = st.sidebar.radio("Navigation", ["💬 LPU Chatbot", "📊 Student Insights"])

    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Common Inquiries:")
    examples = [
        "What is the LPU attendance policy?",
        "tell me fee structure of MCA at lpu",
        "How do scholarships work at LPU?",
        "Book a session with an LPU advisor"
    ]
    for ex in examples:
        if st.sidebar.button(ex):
            st.session_state.messages.append({"role": "user", "content": ex})
            response, intent, sentiment = handle_query(st.session_state.user_id, ex)
            
            # If fallback triggered, add to messages and skip immediate rerun to allow Puter to render
            if "FALLBACK" in response or "SEARCH_FAILURE" in response:
                 st.session_state.messages.append({"role": "assistant", "content": response, "use_puter": True, "puter_prompt": f"As an LPU Academic Advisor, answer: {ex}"})
            else:
                 st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    if page == "💬 LPU Chatbot":
        show_chat()
    else:
        show_dashboard()

def show_chat():
    st.title("🎓 LPU Academic Advisor")
    st.markdown("Welcome to the LPU AI Support. Ask about course recommendations, LPU academic policies, or book an appointment.")

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("use_puter"):
                puter_ai_chat(message.get("puter_prompt", ""))

    # User Input
    if prompt := st.chat_input("How can I help you today?"):
        # 1. Immediately display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Process Assistant Response with professional UI feedback
        with st.chat_message("assistant"):
            with st.status("🦁 LPU Advisor is working...", expanded=True) as status:
                st.write("🔍 Analyzing your inquiry...")
                # Get response
                response, intent, sentiment = handle_query(st.session_state.user_id, prompt)
                
                st.write(f"📖 Searching LPU {intent.replace('_', ' ')} knowledge base...")
                
                use_puter = False
                puter_prompt = ""
                
                # Check if we need Puter synthesis
                if "FALLBACK" in response or "SEARCH_FAILURE" in response or len(response) < 50:
                    st.write("✨ Synthesizing professional LPU advice via Puter AI...")
                    use_puter = True
                    puter_prompt = f"As an LPU Academic Advisor, answer based on university context: {prompt}"
                    status.update(label="✅ Synthesis Complete", state="complete", expanded=False)
                    # Puter bridge renders below the status
                    puter_ai_chat(puter_prompt)
                else:
                    status.update(label="✅ Response Found", state="complete", expanded=False)

                st.markdown(response)
                
                if sentiment > 0.5:
                    st.caption("I'm glad you're feeling positive! 😊")
                elif sentiment < -0.5:
                    st.caption("I'm here to help you through this. 😔")

        # 3. Save assistant response to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response, 
            "use_puter": use_puter, 
            "puter_prompt": puter_prompt
        })
        
        # Avoid full page rerun here to maintain focus

def show_dashboard():
    st.title("📊 Student Interaction Analytics")
    
    fig_intents, fig_sentiment, fig_sentiment_dist, avg_sentiment = get_analytics_data()
    
    if fig_intents is None:
        st.warning("No interaction data available yet. Chat with the bot first!")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig_intents, use_container_width=True)
    
    with col2:
        st.metric("Average Student Sentiment", f"{avg_sentiment:.2f}")
        st.info("Sentiment ranges from -1 (Negative) to 1 (Positive)")
        st.plotly_chart(fig_sentiment_dist, use_container_width=True)

    st.plotly_chart(fig_sentiment, use_container_width=True)

if __name__ == "__main__":
    main()
