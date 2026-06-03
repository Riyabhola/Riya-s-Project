from logic.chatbot import handle_query
import random
import time

def generate_sample_data():
    user_ids = [f"student_{i}" for i in range(1, 11)]
    queries = [
        "Hello!",
        "What is the LPU attendance policy?",
        "I need a recommendation for a CSE course",
        "Can I see an LPU faculty advisor tomorrow?",
        "Tell me about academic probation at LPU",
        "I'm feeling very frustrated with my marks",
        "Thank you for the guidance, LPU Advisor!",
        "What are the credit requirements for graduation at LPU?",
        "Suggest some introductory Python classes",
        "How do I use the UMS portal for registration?",
        "I want to book an LPU advisor meeting",
        "Help me plan my LPU semester",
        "What is the LPUNEST scholarship criteria?",
        "Recommend some management courses at LPU",
        "This LPU assistant is great, thank you!"
    ]

    print("Generating sample interactions...")
    for _ in range(30):
        user_id = random.choice(user_ids)
        query = random.choice(queries)
        handle_query(user_id, query)
        # We don't need a real sleep, just want different timestamps in DB if it was real-time
        # but the DB uses CURRENT_TIMESTAMP which might be the same for all in this loop.
        # Let's just run it.
    
    print("Sample data generated successfully.")

if __name__ == "__main__":
    generate_sample_data()
