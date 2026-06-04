import streamlit as st
import streamlit.components.v1 as components
import os
import uuid
import json
import advisor_logic
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

PUTER_JS_MODEL = os.getenv("PUTER_JS_MODEL", "gpt-5.5")

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


def run_puter_js(prompt: str, model: str = PUTER_JS_MODEL):
    """Render Puter.js in the browser and display the AI response directly in the component."""
    html = f"""
    <div id='puter-status' style='font-family: sans-serif; color: #111; padding: 12px;'>Initializing Puter.js...</div>
    <div id='puter-output' style='font-family: sans-serif; color: #222; white-space: pre-wrap; padding: 12px;'></div>
    <script>
      async function normalizeResult(result) {{
        if (result === null || result === undefined) return '';
        if (typeof result === 'object') {{
          return result.text || result.message || (result.message && result.message.content) || JSON.stringify(result, null, 2);
        }}
        return result.toString();
      }}

      async function loadPuterScript() {{
        if (window.puter && window.puter.ai && window.puter.ai.chat) return;
        return new Promise((resolve, reject) => {{
          const existing = document.getElementById('puter-js-script');
          if (existing) {{
            existing.onload = () => resolve();
            existing.onerror = () => reject(new Error('Failed to load existing puter.js script'));
            return;
          }}
          const script = document.createElement('script');
          script.id = 'puter-js-script';
          script.src = 'https://js.puter.com/v2/';
          script.async = true;
          script.defer = true;
          script.onload = () => resolve();
          script.onerror = () => reject(new Error('Failed to load puter.js'));
          (document.head || document.body || document.documentElement).appendChild(script);
        }});
      }}

      async function runPuter() {{
        const statusNode = document.getElementById('puter-status');
        const outputNode = document.getElementById('puter-output');
        const userPrompt = {json.dumps(prompt)};
        const modelName = {json.dumps(model)};

        try {{
          statusNode.innerText = 'Loading Puter.js...';
          await loadPuterScript();
          if (!window.puter || !window.puter.ai || !window.puter.ai.chat) {{
            throw new Error('Puter SDK did not initialize correctly');
          }}

          statusNode.innerText = 'Using Puter.js model ' + modelName + ' for AI response...';
          let response;
          try {{
            response = await window.puter.ai.chat({{
              model: modelName,
              messages: [{{ role: 'user', content: userPrompt }}]
            }});
          }} catch (firstError) {{
            response = await window.puter.ai.chat(userPrompt);
          }}

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
    return components.html(html, height=420, scrolling=True)

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
            # Use Puter.js in production for substantive LPU academic queries
            should_use_puter = isinstance(res, str) and intent in {
                "general_inquiry",
                "query_policy",
                "get_course_recommendation",
                "identity"
            }

            if should_use_puter:
                use_puter = True
                p_prompt = f"As an LPU Advisor, answer this query using university context: {prompt}"
                st.markdown("**Using free Puter.js AI for enhanced response below.**")
                run_puter_js(p_prompt, PUTER_JS_MODEL)
                res = "(Puter.js response is rendered in the browser component below.)"
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
