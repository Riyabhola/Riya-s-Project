import streamlit as st
import os
import uuid
import pandas as pd
import plotly.express as px
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
    # Professional UX: Disable the default Streamlit grey/fade-out overlay during execution
    st.markdown("""
        <style>
        div[data-stale="true"] {
            opacity: 1 !important;
            filter: none !important;
        }
        [data-stale="true"] > div {
            opacity: 1 !important;
            filter: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

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
                st.markdown("**AI Chatbot is responding to your query.**")
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
        p_prompt = (
            "You are the LPU AI Academic Advisor. Answer the student's query professionally.\n"
            "- If the query is related to LPU policies, courses, admissions, or campus life, answer it using relevant LPU context.\n"
            "- If the query is a general question (e.g. math, general knowledge, programming, general career guidance), answer it directly, accurately, and naturally. Do NOT force LPU context or university metaphors onto simple general questions.\n\n"
            f"Query: {st.session_state.current_prompt}"
        )
        
        # Call client-side custom component loaded with Puter.js
        client_response = puter_client_chat(prompt=p_prompt, key=f"puter_call_{len(st.session_state.messages)}")
        
        if not isinstance(client_response, str):
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
    st.markdown("Academic advisor control panel. Monitor student sentiment, query intents, and Puter AI resolver rates.")
    
    # Fetch raw interaction logs from database
    df_raw = advisor_logic.get_analytics_df()
    if df_raw is None or df_raw.empty:
        st.warning("No interactions registered yet. Start a conversation to generate analytics!")
        return
        
    df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
    
    # 🔍 Interactive Filters Expander
    with st.expander("🔍 Interactive Analytics Filters", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            time_option = st.selectbox(
                "Time Period",
                ["All Time", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
            )
        with f_col2:
            all_intents = sorted(df_raw['intent'].unique().tolist())
            intents_selected = st.multiselect(
                "Filter by Student Intent",
                all_intents,
                default=[]
            )
        with f_col3:
            df_raw['sentiment_cat'] = df_raw['sentiment'].apply(
                lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral')
            )
            sentiments_selected = st.multiselect(
                "Filter by Sentiment",
                ["Positive", "Neutral", "Negative"],
                default=[]
            )
            
    # Apply filters to data
    df = df_raw.copy()
    
    # Time filter
    if time_option != "All Time":
        now_utc = pd.Timestamp.utcnow().tz_localize(None)
        df['timestamp_naive'] = df['timestamp'].dt.tz_localize(None)
        if time_option == "Last 24 Hours":
            df = df[df['timestamp_naive'] >= now_utc - pd.Timedelta(days=1)]
        elif time_option == "Last 7 Days":
            df = df[df['timestamp_naive'] >= now_utc - pd.Timedelta(days=7)]
        elif time_option == "Last 30 Days":
            df = df[df['timestamp_naive'] >= now_utc - pd.Timedelta(days=30)]
            
    # Intent filter
    if intents_selected:
        df = df[df['intent'].isin(intents_selected)]
        
    # Sentiment filter
    if sentiments_selected:
        df = df[df['sentiment_cat'].isin(sentiments_selected)]
        
    # Handle empty filtered state
    if df.empty:
        st.info("No records match the current filter selection.")
        return

    # 1. KPI Ribbon (4 Columns)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Inquiries", len(df))
    with kpi2:
        st.metric("Unique Students", df['user_id'].nunique())
    with kpi3:
        avg_sentiment = df['sentiment'].mean()
        sentiment_label = "Positive" if avg_sentiment > 0.1 else ("Negative" if avg_sentiment < -0.1 else "Neutral")
        st.metric("Average Sentiment", f"{avg_sentiment:+.2f}", delta=sentiment_label)
    with kpi4:
        ai_resolved = len(df[df['intent'] == 'general_inquiry'])
        ai_rate = (ai_resolved / len(df)) * 100 if len(df) > 0 else 0.0
        st.metric("AI Resolver Rate", f"{ai_rate:.1f}%")

    st.markdown("---")

    # 2. Charts Layout - Row 1
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        with st.container(border=True):
            st.markdown("##### 🎯 Intent Distribution")
            intent_counts = df['intent'].value_counts().reset_index()
            intent_counts.columns = ['Intent', 'Count']
            fig_intents = px.pie(
                intent_counts,
                values='Count',
                names='Intent',
                hole=0.6,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_intents.update_traces(textposition='inside', textinfo='percent+label')
            fig_intents.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=280
            )
            st.plotly_chart(fig_intents, theme="streamlit", width="stretch")
            
    with chart_col2:
        with st.container(border=True):
            st.markdown("##### 🎭 Sentiment Volume")
            sentiment_counts = df['sentiment_cat'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment', 'Count']
            color_map = {'Positive': '#2e7d32', 'Neutral': '#757575', 'Negative': '#c62828'}
            fig_dist = px.bar(
                sentiment_counts,
                x='Sentiment',
                y='Count',
                color='Sentiment',
                color_discrete_map=color_map,
                category_orders={"Sentiment": ["Positive", "Neutral", "Negative"]}
            )
            fig_dist.update_layout(
                showlegend=False,
                xaxis_title=None,
                yaxis_title="Queries",
                margin=dict(t=10, b=10, l=10, r=10),
                height=280
            )
            st.plotly_chart(fig_dist, theme="streamlit", width="stretch")

    # 3. Charts Layout - Row 2
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        with st.container(border=True):
            st.markdown("##### 📈 Sentiment Trend Over Time")
            df_sorted = df.sort_values(by='timestamp')
            df_sorted['Rolling Sentiment'] = df_sorted['sentiment'].rolling(
                window=max(1, len(df_sorted)//5), min_periods=1
            ).mean()
            fig_trend = px.area(
                df_sorted,
                x='timestamp',
                y='Rolling Sentiment',
                color_discrete_sequence=['#1976d2']
            )
            fig_trend.update_layout(
                xaxis_title=None,
                yaxis_title="Avg Sentiment (Rolling)",
                margin=dict(t=10, b=10, l=10, r=10),
                height=280
            )
            st.plotly_chart(fig_trend, theme="streamlit", width="stretch")
            
    with chart_col4:
        with st.container(border=True):
            st.markdown("##### ⏰ Student Peak Engagement Hours")
            df['Hour'] = df['timestamp'].dt.hour
            hour_counts = df['Hour'].value_counts().reindex(range(24), fill_value=0).reset_index()
            hour_counts.columns = ['Hour', 'Queries']
            fig_hours = px.bar(
                hour_counts,
                x='Hour',
                y='Queries',
                color='Queries',
                color_continuous_scale=px.colors.sequential.Tealgrn
            )
            fig_hours.update_layout(
                xaxis=dict(tickmode='linear', tick0=0, dtick=4),
                xaxis_title="Hour of Day (24h)",
                yaxis_title="Queries",
                coloraxis_showscale=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=280
            )
            st.plotly_chart(fig_hours, theme="streamlit", width="stretch")

    # 4. Critical Support Alert (Sentiment < -0.3)
    critical_df = df[df['sentiment'] < -0.3].sort_values(by='timestamp', ascending=False)
    if not critical_df.empty:
        st.error(f"⚠️ **Academic Support Alert:** Found {len(critical_df)} inquiries with high negative sentiment. Advisors should check these queries.")
        with st.expander("🔴 View Flagged Student Queries", expanded=False):
            for _, row in critical_df.head(5).iterrows():
                st.markdown(f"**Student ID:** `{row['user_id']}` | **Time:** `{row['timestamp'].strftime('%Y-%m-%d %H:%M')}`")
                st.markdown(f"- **Query:** *\"{row['query']}\"*")
                st.markdown(f"- **Response:** *\"{row['response']}\"*")
                st.markdown(f"- **Sentiment:** `{row['sentiment']:.2f}` | **Intent:** `{row['intent']}`")
                st.markdown("---")

    # 5. Searchable Interactive Data Log
    st.markdown("---")
    st.subheader("📋 Searchable Interaction Log")
    
    display_df = df.copy()
    display_df['Time'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df = display_df[['Time', 'user_id', 'query', 'intent', 'sentiment', 'response']].rename(columns={
        'user_id': 'Student ID',
        'query': 'Student Query',
        'intent': 'Identified Intent',
        'sentiment': 'Sentiment Score',
        'response': 'Bot Response'
    }).sort_values(by='Time', ascending=False)
    
    st.dataframe(display_df, width="stretch")

if __name__ == "__main__":
    main()
