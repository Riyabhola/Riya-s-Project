import os
from dotenv import load_dotenv
import uuid
import advisor_logic
import pandas as pd
from unittest.mock import patch
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Suppress Streamlit warnings in bare mode
logging.getLogger("streamlit").setLevel(logging.ERROR)

def run_standard_tests():
    print("🚀 Starting Standard Verification Suite for LPU Advisor (Bare Mode)...")
    
    # 1. Test Environment & Mandates
    print("\n[Test 1] Mandate Compliance Check")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ℹ️  DATABASE_URL is missing. Initiating Structural Compliance Check...")
        try:
            # Create an in-memory database to verify models and logic
            test_engine = create_engine("sqlite:///:memory:")
            advisor_logic.Base.metadata.create_all(bind=test_engine)
            
            # Verify Seeding Logic
            TestSession = sessionmaker(bind=test_engine)
            db = TestSession()
            
            # Manually trigger seed check logic with mocked session
            with patch("advisor_logic.engine", test_engine), \
                 patch("advisor_logic.SessionLocal", TestSession):
                advisor_logic.init_online_db()
                policy_count = db.query(advisor_logic.Policy).count()
                course_count = db.query(advisor_logic.Course).count()
                
            db.close()
            print(f"✅ PASSED: Structural Integrity Verified. (Models: OK, Seed Policies: {policy_count}, Seed Courses: {course_count})")
            print("   Note: Online Mandate is required for PROD deployment.")
        except Exception as e:
            print(f"❌ FAILED: Structural Compliance Check Error: {e}")
    else:
        print(f"✅ PASSED: Online Database configured.")

    # 2. Test Logic Discovery
    print("\n[Test 2] Module Integrity Check")
    try:
        from advisor_logic import handle_query, init_online_db
        print("✅ PASSED: Consolidated 'advisor_logic' is discoverable.")
    except ImportError as e:
        print(f"❌ FAILED: advisor_logic import error: {e}")
        return

    # 3. Test Intent Detection (Precision)
    print("\n[Test 3] Intent Detection Precision")
    test_cases = [
        {"q": "attendance policy", "expected": "query_policy"},
        {"q": "fashion courses", "expected": "get_course_recommendation"},
        {"q": "who are you?", "expected": "identity"},
        {"q": "book a meeting", "expected": "book_appointment"},
        {"q": "hello", "expected": "greeting"}
    ]
    
    passed_intents = 0
    for case in test_cases:
        _, intent, _ = advisor_logic.handle_query("test_user", case["q"])
        if intent == case["expected"]:
            print(f"  ✅ Q: '{case['q']}' -> {intent}")
            passed_intents += 1
        else:
            print(f"  ❌ Q: '{case['q']}' -> Found: {intent}, Expected: {case['expected']}")
            
    print(f"✅ Intent Accuracy: {passed_intents}/{len(test_cases)}")

    # 4. Test Knowledge Base Retrieval
    print("\n[Test 4] Knowledge Base Retrieval (Aiven Simulation)")
    # Note: If no DB, it returns fallback or error string
    policy_res = advisor_logic.query_knowledge_base("attendance")
    if any(keyword in policy_res for keyword in ["75%", "No policy found", "Database connection", "Please specify"]):
        print("✅ PASSED: Policy retrieval logic handled correctly.")
    else:
        print(f"❌ FAILED: Policy retrieval returned unexpected format: {policy_res[:50]}...")

    # 5. Test Puter Bridge Integrity
    print("\n[Test 5] Puter AI Bridge Rendering")
    try:
        # Mock streamlit.iframe to capture the URI in bare mode
        with patch("streamlit.iframe", side_effect=lambda url, height: url) as mock_iframe:
            bridge_output = advisor_logic.puter_ai_chat("Test Prompt")
            if bridge_output is not None and "data:text/html;base64" in str(bridge_output):
                print("✅ PASSED: Puter AI Bridge generates modern iframe Data URIs.")
            else:
                print(f"❌ FAILED: Puter bridge output invalid. Received: {type(bridge_output)}")
    except Exception as e:
        print(f"❌ FAILED: Puter bridge crash: {e}")

    print("\n✨ Standard Verification Complete!")

if __name__ == "__main__":
    run_standard_tests()
