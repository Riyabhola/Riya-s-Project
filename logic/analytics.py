import pandas as pd
import plotly.express as px
from logic.database import get_interactions

def get_analytics_data():
    df = get_interactions()
    if df.empty:
        return None, None, None, None
    
    # 1. Intent Distribution
    intent_counts = df['intent'].value_counts().reset_index()
    intent_counts.columns = ['intent', 'count']
    fig_intents = px.pie(intent_counts, values='count', names='intent', title='Interaction by Intent', hole=0.4)
    fig_intents.update_traces(textposition='inside', textinfo='percent+label')
    
    # 2. Sentiment Over Time
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    fig_sentiment = px.line(df, x='timestamp', y='sentiment', title='Student Sentiment Over Time', markers=True)
    fig_sentiment.update_layout(yaxis_range=[-1.1, 1.1])
    
    # 3. Sentiment Distribution
    df['sentiment_category'] = df['sentiment'].apply(lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral'))
    sentiment_dist = df['sentiment_category'].value_counts().reset_index()
    sentiment_dist.columns = ['Category', 'Count']
    fig_sentiment_dist = px.bar(sentiment_dist, x='Category', y='Count', title='Sentiment Distribution', color='Category',
                               color_discrete_map={'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'})
    
    # 4. Sentiment Summary
    avg_sentiment = df['sentiment'].mean()
    
    return fig_intents, fig_sentiment, fig_sentiment_dist, avg_sentiment
