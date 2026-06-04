# 🦁 LPU AI Academic Advisor - Architecture & Data Flow

## 1. System Overview
The **LPU AI Academic Advisor (Quantum Edition)** is a professional-grade intelligent assistant designed for Lovely Professional University. It combines high-precision knowledge retrieval with advanced AI synthesis via the **Quantum Bridge**.

## 2. Architectural Components

### 🏛️ Core Logic Engine (`advisor_logic.py`)
- **Intent Detection:** Hybrid logic using keyword matching and sentiment context.
- **Synthesis Engine:** Orchestrates the flow between local knowledge and AI-enhanced synthesis.
- **Analytics Tracker:** Real-time logging of student sentiment and query distribution.

### 🌉 Quantum Bridge (`puter_auth_service.py`)
- **Zero-Interaction Auth:** Server-side handshake using Puter REST API.
- **AI Synthesis:** Direct headless integration with Puter AI (GPT-3.5/4).
- **Fallback Resilience:** Automatic failover to OpenAI to ensure 100% service availability.

### 🗄️ Persistence Layer (Aiven PostgreSQL)
- **Production-Ready:** Enterprise PostgreSQL hosted on Aiven.
- **Schema Management:** Automated migrations and seeding from `data/*.csv`.
- **Data Encapsulation:**
    - `policies`: Authoritative LPU academic guidelines.
    - `courses`: LPU department-specific course database.
    - `interactions`: Audit trail for student queries and AI responses.
    - `appointments`: Future-ready scheduling for student-advisor meetings.

## 3. Data Flow Orchestration

1. **Student Interaction:** User submits a query via the Streamlit LPU Chatbot interface.
2. **Knowledge Retrieval:** The system performs a primary search against the **Aiven PostgreSQL** knowledge base.
3. **AI Synthesis (The Quantum Bridge):** 
   - If the local guidance is sufficient, it is delivered immediately.
   - If deeper synthesis is required, the **Quantum Bridge** executes a background AI handshake.
4. **Sentiment Analytics:** Every response is analyzed for polarity and recorded for institutional insights.
5. **Dynamic Dashboarding:** The analytics engine visualizes data trends for university administrators.

## 4. Performance & Security
- **Latency:** Sub-second response times across all components.
- **Security:** TLS/SSL encrypted database connections and token-based AI authentication.
- **Reliability:** Dual-engine AI failover and multi-region database replication.
