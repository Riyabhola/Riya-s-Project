import streamlit as st
import os
import uuid
import advisor_logic
from dotenv import load_dotenv
from puter_auth_service import puter_client_chat

# Load environment variables
load_dotenv(override=True)



# Set DATABASE_URL if not already present in environment
if "DATABASE_URL" not in os.environ:
    try:
        if "DATABASE_URL" in st.secrets:
            os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
    except Exception:
        pass

# Page Configuration
st.set_page_config(page_title="LPU Academic Advisor", layout="wide")

# Initialize Online Database
try:
    advisor_logic.init_online_db()
except Exception as e:
    st.error(f"Critical System Error: Database connection failed. Please ensure DATABASE_URL is set correctly. ({e})")
    st.stop()

# Session State for Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = None
if "current_intent" not in st.session_state:
    st.session_state.current_intent = None
if "current_sentiment" not in st.session_state:
    st.session_state.current_sentiment = None


def main():
    st.sidebar.title("🦁 LPU Advisor Hub")
    st.sidebar.info("Dedicated AI Advisor for Lovely Professional University students.")
    
    page = st.sidebar.radio("Navigation", ["💬 LPU Chatbot", "📊 Student Insights"])

    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.current_prompt = None
        st.session_state.current_intent = None
        st.session_state.current_sentiment = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Common Inquiries:")
    examples = ["Attendance policy", "Scholarships", "Fashion courses", "Book appointment"]
    for ex in examples:
        if st.sidebar.button(ex):
            st.session_state.messages.append({"role": "user", "content": ex})
            st.rerun()

    if page == "💬 LPU Chatbot":
        show_chat()
    else:
        show_dashboard()

def process_message(prompt):
    # Immediate user feedback
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

def show_chat():
    st.title("🎓 LPU Academic Advisor")
    st.markdown("Welcome to LPU AI Support. High-precision guidance for your academic journey.")

    # Render history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("use_puter"):
                st.markdown("**Using seamless server-side Puter AI for enhanced response below.**")
            st.markdown(message["content"])

    # Input
    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Chat execution state machine
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_query = st.session_state.messages[-1]["content"]
        
        if st.session_state.current_prompt is None:
            # Determine intent and local response
            res, intent, sentiment = advisor_logic.handle_query(st.session_state.user_id, user_query)
            
            if res == "__USE_PUTER__":
                # Set transition to client-side Puter.js flow
                st.session_state.current_prompt = user_query
                st.session_state.current_intent = intent
                st.session_state.current_sentiment = sentiment
                st.rerun()
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": res,
                    "use_puter": False,
                    "puter_prompt": ""
                })
                st.rerun()

    # Client-Side Puter.js Flow
    if st.session_state.current_prompt is not None:
        p_prompt = f"As an LPU Advisor, answer this query using university context: {st.session_state.current_prompt}"
        
        # Call client-side custom component loaded with Puter.js
        client_response = puter_client_chat(prompt=p_prompt, key=f"puter_call_{len(st.session_state.messages)}")
        
        if client_response is None:
            # Component is running in browser, display loader
            with st.chat_message("assistant"):
                st.info("🦁 Advisor is searching (Client-Side Puter.js)...")
        else:
            # Graceful server-side fallback if client-side Puter.js fails
            if client_response.startswith("Error from Puter.js:"):
                client_response = advisor_logic.puter_ai_chat(p_prompt)
                
            # Log the Puter interaction in Aiven Postgres
            advisor_logic.log_interaction(
                st.session_state.user_id,
                st.session_state.current_prompt,
                st.session_state.current_intent,
                client_response,
                st.session_state.current_sentiment
            )
            
            # Save the message and reset
            st.session_state.messages.append({
                "role": "assistant",
                "content": client_response,
                "use_puter": True,
                "puter_prompt": p_prompt
            })
            st.session_state.current_prompt = None
            st.session_state.current_intent = None
            st.session_state.current_sentiment = None
            st.rerun()

def show_dashboard():
    st.title("📊 Student Insights Dashboard")
    st.markdown("Executive overview of AI-student interactions and university academic sentiment.")
    
    # Fetch enhanced data
    data = advisor_logic.get_analytics_data()
    if data[0] is None:
        st.warning("Start a conversation to see analytics!")
        return
    
    fig_intents, fig_sentiment, fig_dist, avg_sentiment, metrics = data

    # 1. KPI Ribbon
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Total Inquiries", metrics['total'], delta=None)
    with kpi2:
        sentiment_label = "Positive" if avg_sentiment > 0.1 else ("Negative" if avg_sentiment < -0.1 else "Neutral")
        st.metric("Average Sentiment", f"{avg_sentiment:.2f}", delta=sentiment_label)
    with kpi3:
        st.metric("Top Student Concern", metrics['top'].replace('_', ' ').title())

    st.markdown("---")

    # 2. Primary Analytics Row
    col1, col2 = st.columns([1, 1.5])
    with col1:
        with st.container(border=True):
            st.plotly_chart(fig_intents, use_container_width=True)
    with col2:
        with st.container(border=True):
            st.plotly_chart(fig_dist, use_container_width=True)

    # 3. Time Series Analytics
    with st.container(border=True):
        st.plotly_chart(fig_sentiment, use_container_width=True)

if __name__ == "__main__":
    main()
