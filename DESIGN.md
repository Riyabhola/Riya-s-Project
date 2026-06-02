# AI-Powered Academic Advising Chatbot Design

## Overview
An academic advising chatbot built with Streamlit, leveraging Dialogflow for intent recognition and ChromaDB for RAG-based knowledge retrieval.

## Architecture
- **Frontend:** Streamlit (Chat UI + Analytics Dashboard)
- **NLP Engine:** Google Dialogflow (Intent handling)
- **Knowledge Base:** ChromaDB (Vector database for academic policies)
- **Data Persistence:** SQLite (Student records, interaction logs, appointments)
- **Sentiment Analysis:** TextBlob / NLTK

## Key Components

### 1. Chatbot Interface
- Multi-turn conversation logic.
- Intent mapping:
    - `get_course_recommendation`
    - `query_policy`
    - `book_appointment`
    - `general_inquiry`

### 2. Knowledge Base (RAG)
- Academic policies (grading, credits, graduation requirements) stored as embeddings in ChromaDB.
- Semantic search to retrieve relevant policy text for student queries.

### 3. Recommendation Engine
- Logic to suggest courses based on student profile (major, year, interests).

### 4. Appointment System
- Integration with a mock booking service, storing data in SQLite.

### 5. Analytics Dashboard
- Visualization of student sentiment over time.
- Most frequent topics/intents.
- Scheduling trends.

## Data Flow
1. User enters query in Streamlit.
2. Query sent to Dialogflow for intent detection.
3. If intent is `query_policy`, query ChromaDB for context.
4. Response generated based on Dialogflow/RAG logic.
5. Interaction logged to SQLite for analytics.
6. Display response in Streamlit.
