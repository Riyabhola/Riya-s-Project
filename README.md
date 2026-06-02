# 🎓 Academic Advising AI Chatbot

![Python CI](https://github.com/<your-username>/academic-advising-chatbot/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/<your-username>/academic-advising-chatbot)

An AI-powered academic advising system built with **Streamlit**, **ChromaDB (RAG)**, and **TextBlob**. This system provides course recommendations, academic policy guidance, and automated appointment scheduling.

## 🚀 Features
- **Intelligent Chatbot:** Detects student intents and provides context-aware responses.
- **RAG Knowledge Base:** Semantic search on university policies using ChromaDB.
- **Course Recommendations:** Personalized suggestions based on department and interest.
- **Appointment Booking:** Simulated integration with advisor scheduling.
- **Analytics Dashboard:** Real-time tracking of student sentiment and interaction trends.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Vector DB:** ChromaDB (Sentence Transformers)
- **Sentiment Analysis:** TextBlob
- **Data Visualization:** Plotly
- **Database:** SQLite

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/academic-advising-chatbot.git
   cd academic-advising-chatbot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 🧪 Testing
To run the conversational accuracy tests:
```bash
python logic/test_accuracy.py
```

## 📊 Sample Data
The project includes a sample data generator to populate the analytics dashboard:
```bash
python logic/generate_sample_data.py
```

## 🤝 Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License
This project is licensed under the [MIT License](LICENSE).

## 🌐 Deployment (Streamlit Cloud)
1. Push this repository to GitHub.
2. Connect your GitHub account to [Streamlit Cloud](https://streamlit.io/cloud).
3. Select this repository and the `app.py` file.
4. Click **Deploy**.
