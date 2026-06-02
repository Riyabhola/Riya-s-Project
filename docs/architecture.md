# Academic Advising Chatbot Architecture & API Flow

## 1. System Components
- **Streamlit Frontend:** Low-code interface for student interaction and advisor dashboard.
- **NLP Layer (Keyword-based / Dialogflow Ready):** Detects user intent (Recommendations, Policies, Booking, Greetings).
- **RAG Knowledge Base (ChromaDB):** Retrieves academic policies using vector embeddings (Sentence Transformers).
- **Analytics Engine:** Processes interaction logs and performs sentiment analysis using TextBlob.
- **Persistence Layer (SQLite):** Stores student records, logs, and appointments.

## 2. API & Data Flow
1. **User Query:** Student submits a question in the Streamlit UI.
2. **Intent Detection:** Query is processed to identify the goal (e.g., `query_policy`).
3. **Information Retrieval:**
   - If policy query: ChromaDB performs semantic search on university policy docs.
   - If recommendation: Dynamic filtering on `courses.csv` based on department/level keywords.
   - If booking: SQLite update to `appointments` table with simulated advisor assignment.
4. **Sentiment Analysis:** TextBlob analyzes the tone of the student's message (Polarity).
5. **Logging:** Every turn is recorded in `academic_advising.db` for the analytics dashboard.
6. **Response Generation:** The system combines retrieved data into a natural language response with interactive feedback.

## 3. Analytics Dashboard
- **Intent Distribution:** Pie chart showing most common student needs.
- **Sentiment Trends:** Line chart tracking student mood over time.
- **Sentiment Distribution:** Bar chart categorizing interactions as Positive, Neutral, or Negative.
- **Key Metrics:** Average sentiment score.
