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
    st.sidebar.info("Dedicated AI Advisor for Lovely Professional University students. 100% Cloud-Native & Puter-Powered.")
    
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
    st.title("📊 Student Interaction Analytics")
    fig1, fig2, fig3, avg = advisor_logic.get_analytics_data()
    if fig1 is None:
        st.warning("Start a conversation to see analytics!")
        return
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(fig1, use_container_width=True)
    with c2: 
        st.metric("Avg Sentiment", f"{avg:.2f}")
        st.plotly_chart(fig3, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()
