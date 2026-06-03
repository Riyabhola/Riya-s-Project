# LPU AI-Powered Academic Advising Chatbot Design

## Overview
An academic advising chatbot specifically tailored for **Lovely Professional University (LPU)**, leveraging Dialogflow for intent recognition and ChromaDB for RAG-based knowledge retrieval of LPU policies.

## Architecture
- **Frontend:** Streamlit (LPU branded Chat UI + Student Insights Dashboard)
- **NLP Engine:** Google Dialogflow / Keyword-based Mock (LPU intent handling)
- **Knowledge Base:** ChromaDB (Vector database for LPU academic policies)
- **Data Persistence:** SQLAlchemy (Supports SQLite local and PostgreSQL cloud for LPU logs)
- **Sentiment Analysis:** TextBlob

## Key Components

### 1. LPU Chatbot Interface
- Multi-turn conversation logic with university-specific tone.
- Intent mapping:
    - `get_course_recommendation` (LPU specific)
    - `query_policy` (Attendance, Scholarships, UMS)
    - `book_appointment` (LPU Faculty Advisors)
    - `general_inquiry`

### 2. LPU Knowledge Base (RAG)
- LPU academic policies (75% attendance rule, LPUNEST scholarships, UMS registration) stored in ChromaDB.
- Semantic search to provide authoritative LPU-specific answers.

### 3. Recommendation Engine
- Logic to suggest LPU courses (CSE, Management, Biotechnology) based on student interests.

### 4. Professional Persistence Layer
- Hybrid database model (SQLAlchemy) allowing local development and cloud production deployments (e.g., Aiven, Supabase).
