import streamlit as st
import os
import uuid
import advisor_logic

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

def main():
    st.sidebar.title("🦁 LPU Advisor Hub")
    st.sidebar.info("Dedicated AI Advisor for Lovely Professional University students.")
    
    page = st.sidebar.radio("Navigation", ["💬 LPU Chatbot", "📊 Student Insights"])

    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Common Inquiries:")
    examples = ["Attendance policy", "Scholarships", "Fashion courses", "Book appointment"]
    for ex in examples:
        if st.sidebar.button(ex):
            process_message(ex)

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
            st.markdown(message["content"])
            if message.get("use_puter"):
                advisor_logic.puter_ai_chat(message.get("puter_prompt", ""))

    # Input
    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("🦁 Advisor is searching...", expanded=False) as status:
                res, intent, sentiment = advisor_logic.handle_query(st.session_state.user_id, prompt)
                status.update(label="✅ Guidance Found", state="complete")
            
            use_puter = False
            p_prompt = ""
            if len(res) < 50 or "No policy" in res or "No matching" in res:
                use_puter = True
                p_prompt = f"As an LPU Advisor, answer this query using university context: {prompt}"
                advisor_logic.puter_ai_chat(p_prompt)
            
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res, "use_puter": use_puter, "puter_prompt": p_prompt})

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
