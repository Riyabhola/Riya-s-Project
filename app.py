import os
# Force pure Python implementation of protobuf for Python 3.14 compatibility
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import streamlit as st
from logic.chatbot import handle_query
from logic.analytics import get_analytics_data
from logic.database import init_sqlite, init_chroma
import uuid

# Initialize databases on startup
init_sqlite()
init_chroma()

st.set_page_config(page_title="Academic Advising AI", layout="wide")

# Session State for Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Chatbot", "Analytics Dashboard"])

    if page == "Chatbot":
        show_chat()
    else:
        show_dashboard()

def show_chat():
    st.title("🎓 Academic Advising Chatbot")
    st.markdown("Ask me about course recommendations, policies, or book an appointment.")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response, intent, sentiment = handle_query(st.session_state.user_id, prompt)
            st.markdown(response)
            
            # Optional feedback in UI
            if sentiment > 0.5:
                st.caption("I'm glad you're feeling positive! 😊")
            elif sentiment < -0.5:
                st.caption("I'm sorry you're feeling frustrated. I'm here to help. 😔")

        st.session_state.messages.append({"role": "assistant", "content": response})

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
