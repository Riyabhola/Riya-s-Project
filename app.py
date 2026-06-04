import streamlit as st
import streamlit.components.v1 as components
import os
import uuid
import json
import advisor_logic
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

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


def run_puter_js(prompt: str):
    """Render Puter.js in the browser and display the AI response directly in the component."""
    html = f"""
    <div id='puter-status' style='font-family: sans-serif; color: #111; padding: 12px;'>Initializing Puter.js...</div>
    <div id='puter-output' style='font-family: sans-serif; color: #222; white-space: pre-wrap; padding: 12px;'></div>
    <script>
      async function normalizeResult(result) {{
        if (result === null || result === undefined) return '';
        if (typeof result === 'object') {{
          return result.text || result.message || JSON.stringify(result, null, 2);
        }}
        return result.toString();
      }}
      async function runPuter() {{
        const outputNode = document.getElementById('puter-output');
        const statusNode = document.getElementById('puter-status');
        try {{
          statusNode.innerText = 'Loading Puter.js...';
          const userPrompt = {json.dumps(prompt)};
          if (!window.puter || !window.puter.ai || !window.puter.ai.chat) {{
            await new Promise((resolve, reject) => {{
              const script = document.createElement('script');
              script.src = 'https://js.puter.com/v2/';
              script.onload = () => resolve();
              script.onerror = () => reject(new Error('Failed to load puter.js'));
              document.head.appendChild(script);
            }});
          }}
          statusNode.innerText = 'Using Puter.js for AI response...';
          const response = await window.puter.ai.chat(userPrompt);
          const normalized = await normalizeResult(response);
          statusNode.innerText = '✅ Free Puter.js AI response';
          outputNode.innerText = normalized || 'No response received from Puter.js.';
        }} catch (error) {{
          statusNode.innerText = '⚠️ Puter.js error';
          outputNode.innerText = 'PUTERJS_ERROR: ' + (error?.message || error?.toString() || 'Unknown error');
        }}
      }}
      runPuter();
    </script>
    """
    return components.html(html, height=360, scrolling=True)

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
            st.session_state.messages.append({"role": "user", "content": ex})
            res, intent, sentiment = advisor_logic.handle_query(st.session_state.user_id, ex)
            st.session_state.messages.append({"role": "assistant", "content": res, "use_puter": False, "puter_prompt": ""})
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
            st.markdown(message["content"])

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
            # If the initial response is too short or no policy found, enhance with AI
            should_use_puter = isinstance(res, str) and (
                len(res) < 50 or
                "No policy" in res or
                "No matching" in res or
                (intent == "identity" and any(term in prompt.lower() for term in ["where", "were you", "location", "been"]))
            )
            if should_use_puter:
                use_puter = True
                p_prompt = f"As an LPU Advisor, answer this query using university context: {prompt}"
                st.markdown("**Using free Puter.js AI for enhanced response below.**")
                run_puter_js(p_prompt)
                res = "(Puter.js response is rendered below in the browser component.)"
            else:
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
