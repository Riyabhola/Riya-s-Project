from logic.chatbot import handle_query
import random
import time

def generate_sample_data():
    user_ids = [f"student_{i}" for i in range(1, 11)]
    queries = [
        "Hi there",
        "What is the grading scale?",
        "I need a recommendation for a computer science course",
        "Can I see an advisor tomorrow?",
        "Tell me about academic probation",
        "I'm feeling very frustrated with my grades",
        "Thank you for the help!",
        "What are the credit requirements for graduation?",
        "Suggest some introductory math classes",
        "How do I declare a major?",
        "I want to book a meeting",
        "Help me plan my semester",
        "What happens if I get an incomplete grade?",
        "Recommend some biology courses",
        "This is great, thank you!"
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
