# Project: LPU Academic Advising Chatbot (Puter AI Edition)

## Tech Stack
- **Frontend/App:** Streamlit
- **AI Engine:** Puter.js (100% Automated/Keyless Browser Integration)
- **Backend AI:** Puter GenAI SDK (GPT-4o Mini)
- **Database:** Aiven PostgreSQL (Exclusive Online Knowledge Base & Storage)
- **Analytics:** Pandas/Plotly
- **Sentiment:** TextBlob

## File Structure
- `app.py`: Main LPU branded Streamlit application.
- `logic/`: Backend logic.
    - `chatbot.py`: LPU intent detection and Puter AI orchestration.
    - `database.py`: Aiven PostgreSQL management (no local storage).
    - `analytics.py`: Sentiment and interaction processing.
- `data/`: Placeholder for data migration (CSV files are migrated to Aiven).
- `docs/`: Architecture diagrams and API documentation.

## Environment Configuration
- **Mandatory Variables:**
    - `DATABASE_URL`: Aiven PostgreSQL connection string.
    - `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION`: Set to `python` to resolve Protobuf compatibility issues.
- **Optional Variables:**
    - `PUTER_TOKEN`: For authenticated Puter AI access (guest mode is used as fallback).

## Guidelines
- **100% Online Persistence:** All interactions, appointments, policies, and courses MUST be stored and retrieved from Aiven PostgreSQL.
- **Zero Local Data:** No SQLite, No ChromaDB, No local CSV dependency at runtime.
- **Puter AI Only:** Gemini is strictly prohibited. All synthesis must use Puter's automated browser or SDK guest modes.
- **University Context:** Ensure 75% attendance rule and LPUNEST scholarship logic are strictly followed.
