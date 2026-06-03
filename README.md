# 🎓 LPU AI Academic Advisor (Puter Edition)

[![CI Status](https://github.com/Riyabhola/Riya-s-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/Riyabhola/Riya-s-Project/actions/workflows/ci.yml)
[![Live App](https://img.shields.io/badge/Streamlit-Live%20App-red?logo=streamlit)](https://riyabot.streamlit.app/)
[![License](https://img.shields.io/github/license/Riyabhola/Riya-s-Project)](LICENSE)

A high-performance, **100% automated** AI Academic Advisor for Lovely Professional University. Featuring an innovative **Shadow Proxy** integration for seamless, zero-interaction Puter AI synthesis.

## 🚀 Key Innovations
- **Seamless Puter AI Bypass:** Implements a sophisticated "Shadow Proxy" approach using **MutationObservers** and visibility-safe automation to eliminate user login prompts.
- **Keyless AI Synthesis:** Leverages Puter.js v2 for GPT-4o Mini synthesis without requiring manual API key management from the end-user.
- **Enterprise RAG Engine:** Semantic search powered by **Aiven PostgreSQL** (Online DB) for authoritative LPU policy and course guidance.
- **Real-time Analytics:** Advanced student sentiment tracking and interaction heatmaps using Plotly and TextBlob.

## 🛠️ Tech Stack
- **Frontend:** Streamlit (Custom LPU Branding)
- **AI Engine:** Puter.js v2 (Automated GPT-4o Mini)
- **Database:** Aiven PostgreSQL (Online-only persistence)
- **Analytics:** Pandas, Plotly Express
- **Sentiment:** TextBlob (Linguistic NLP)

## 📦 Architecture Highlights
- **Zero Local Data:** Mandated online persistence to prevent local storage dependency in production environments.
- **Stealth UX:** Aggressive CSS and JavaScript injection to provide a white-labeled, professional advising experience.
- **Auto-Sync:** Fully integrated GitHub Actions CI/CD for instant deployment to Streamlit Cloud.

## 🧪 Quick Start & Testing

1. **Clone & Install:**
   ```bash
   git clone https://github.com/Riyabhola/Riya-s-Project.git
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   Create a `.env` file with your `DATABASE_URL` (Aiven PostgreSQL).

3. **Verify Integrity:**
   Run the comprehensive E2E verification suite:
   ```bash
   python verification_suite.py
   ```

4. **Launch Hub:**
   ```bash
   streamlit run app.py
   ```

## 📜 Project Mandates
Detailed architectural guidelines and AI integration strategies are documented in [PUTER_ADVISOR.md](PUTER_ADVISOR.md).

---
*Built with ❤️ for the LPU Student Community.*
