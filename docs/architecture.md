# LPU Academic Advising Chatbot Architecture & API Flow

## 1. System Components
- **Streamlit Frontend:** Tailored interface for Lovely Professional University (LPU) students.
- **NLP Layer (Keyword-based / Dialogflow Ready):** Detects LPU-specific intents (Attendance, Scholarships, Course Recommendations).
- **RAG Knowledge Base (ChromaDB):** Retrieves LPU university policies from `data/policies.csv`.
- **Analytics Engine:** Processes LPU student interaction logs and sentiment.
- **Persistence Layer (Aiven PostgreSQL):** Stores LPU student interaction data and faculty advisor appointments exclusively in the cloud.

## 2. API & Data Flow
1. **User Query:** Student submits a question in the Streamlit UI.
2. **Intent Detection:** Query is processed to identify the goal (e.g., `query_policy`).
3. **Information Retrieval:**
   - If policy query: ChromaDB performs semantic search on university policy docs.
   - If recommendation: ChromaDB performs semantic search on `courses.csv` data to find relevant matches based on student interests and course descriptions.
   - If booking: PostgreSQL update to `appointments` table with simulated advisor assignment.
4. **Sentiment Analysis:** TextBlob analyzes the tone of the student's message (Polarity).
5. **Logging:** Every turn is recorded in Aiven PostgreSQL for the analytics dashboard.
6. **Response Generation:** The system combines retrieved data into a natural language response with interactive feedback.

## 3. Analytics Dashboard
- **Intent Distribution:** Pie chart showing most common student needs.
- **Sentiment Trends:** Line chart tracking student mood over time.
- **Sentiment Distribution:** Bar chart categorizing interactions as Positive, Neutral, or Negative.
- **Key Metrics:** Average sentiment score.
