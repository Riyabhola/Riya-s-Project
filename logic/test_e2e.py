import sys
import os
import uuid
import pandas as pd
from logic.chatbot import handle_query
from logic.database import init_sqlite, init_chroma, get_interactions
from logic.analytics import get_analytics_data

def test_e2e_flow():
    print("🚀 Starting End-to-End Test for LPU Academic Advisor...")
    
    # 1. Initialize Databases
    print("\n[Step 1] Initializing Databases...")
    init_sqlite()
    init_chroma()
    print("✅ Databases ready.")

    # 2. Simulate User Journey
    user_id = str(uuid.uuid4())
    test_scenarios = [
        {"query": "Hello", "description": "Greeting"},
        {"query": "What is the attendance policy at LPU?", "description": "Policy Query"},
        {"query": "Recommend some CSE courses", "description": "Course Recommendation"},
        {"query": "Book an appointment with an advisor", "description": "Appointment Booking"},
        {"query": "I am very happy with the guidance!", "description": "Positive Feedback"}
    ]

    print(f"\n[Step 2] Simulating User Journey (User ID: {user_id})...")
    for scenario in test_scenarios:
        print(f"👉 Query: '{scenario['query']}' ({scenario['description']})")
        response, intent, sentiment = handle_query(user_id, scenario['query'])
        print(f"   Response: {response[:100]}...")
        print(f"   Intent: {intent} | Sentiment: {sentiment:.2f}")

    # 3. Verify Database Persistence
    print("\n[Step 3] Verifying Database Persistence...")
    df = get_interactions()
    user_logs = df[df['user_id'] == user_id]
    if len(user_logs) == len(test_scenarios):
        print(f"✅ Success: {len(user_logs)} interactions logged correctly.")
    else:
        print(f"❌ Error: Expected {len(test_scenarios)} logs, but found {len(user_logs)}.")
        sys.exit(1)

    # 4. Verify Analytics Generation
    print("\n[Step 4] Verifying Analytics Engine...")
    fig_intents, fig_sentiment, fig_sentiment_dist, avg_sentiment = get_analytics_data()
    if all(v is not None for v in [fig_intents, fig_sentiment, fig_sentiment_dist, avg_sentiment]):
        print(f"✅ Success: Analytics charts and metrics generated.")
        print(f"📊 Average Session Sentiment: {avg_sentiment:.2f}")
    else:
        print("❌ Error: Analytics engine failed to produce visual data.")
        sys.exit(1)

    print("\n✨ E2E Test Passed Successfully!")

if __name__ == "__main__":
    # Ensure project root is in path
    sys.path.append(os.getcwd())
    try:
        test_e2e_flow()
    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")
        sys.exit(1)
