# Project: LPU Academic Advising Chatbot

## Tech Stack
- **Frontend/App:** Streamlit
- **NLP:** Keyword-based Mock + Puter AI Synthesis
- **AI Engine:** Puter.js (100% Automated/Keyless)
- **Vector DB:** ChromaDB (RAG for LPU Policies)
- **Database:** Aiven PostgreSQL (Exclusive Online Storage)
- **Analytics:** Pandas/Plotly
- **Sentiment:** TextBlob

## File Structure
- `app.py`: Main LPU branded Streamlit application.
- `logic/`: Backend logic.
    - `chatbot.py`: LPU intent detection and RAG orchestration.
    - `database.py`: SQLAlchemy and ChromaDB management.
    - `analytics.py`: Sentiment and interaction processing.
- `data/`: LPU specific datasets (CSV/JSON).
- `docs/`: Architecture diagrams and API documentation.

## Guidelines
- All interactions must be logged to `student_interactions.db` (local) or Cloud DB (PostgreSQL).
- Use modular functions for LPU-specific policy retrieval.
- Ensure 75% attendance rule and LPUNEST scholarship logic are strictly followed.
