# Project: Academic Advising Chatbot

## Tech Stack
- **Frontend/App:** Streamlit
- **NLP:** Dialogflow (Python SDK)
- **Vector DB:** ChromaDB
- **Analytics:** Pandas/Plotly
- **Sentiment:** TextBlob

## File Structure
- `app.py`: Main Streamlit application.
- `logic/`: Backend logic.
    - `chatbot.py`: Dialogflow and RAG orchestration.
    - `database.py`: SQLite and ChromaDB management.
    - `analytics.py`: Sentiment and interaction processing.
- `data/`: Sample datasets (CSV/JSON).
- `docs/`: Architecture diagrams and API documentation.

## Guidelines
- Use modular functions in `logic/`.
- Ensure mock support for Dialogflow to allow testing without live credentials.
- All interactions must be logged to `data/student_interactions.db`.
