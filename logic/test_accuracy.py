from logic.chatbot import handle_query
import pandas as pd

def run_tests():
    test_cases = [
        {"query": "What is the LPU attendance policy?", "expected_intent": "query_policy"},
        {"query": "Recommend some Python programming courses at LPU", "expected_intent": "get_course_recommendation"},
        {"query": "Book an appointment with an LPU advisor", "expected_intent": "book_appointment"},
        {"query": "How do scholarships work?", "expected_intent": "query_policy"},
        {"query": "Hi there", "expected_intent": "greeting"}
    ]
    
    results = []
    for case in test_cases:
        response, intent, sentiment = handle_query("test_user", case["query"])
        status = "PASSED" if intent == case["expected_intent"] else "FAILED"
        results.append({
            "Query": case["query"],
            "Detected Intent": intent,
            "Expected": case["expected_intent"],
            "Status": status
        })
    
    df_results = pd.DataFrame(results)
    print("\n--- Conversational Accuracy Test Results ---")
    print(df_results)
    
    accuracy = (df_results['Status'] == 'PASSED').mean() * 100
    print(f"\nOverall Accuracy: {accuracy}%")

if __name__ == "__main__":
    run_tests()
