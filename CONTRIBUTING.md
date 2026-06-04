# Contributing to Academic Advising AI Chatbot

First off, thank you for considering contributing to this project!

## How Can I Contribute?

### Reporting Bugs
* Check the existing issues to see if the bug has already been reported.
* If not, open a new issue using the Bug Report template.

### Suggesting Enhancements
* Open a new issue using the Feature Request template.

### Pull Requests
1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Ensure your code follows the project's style.
4. Run tests: `python verification_suite.py`
5. Submit a pull request!

## Development Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment: `copy .env.example .env` and fill in your credentials.
4. Run the app: `streamlit run app.py`

## Project Structure
- `app.py`: Main entry point (Streamlit UI).
- `advisor_logic.py`: Consolidated business logic, AI orchestration, and database interactions.
- `verification_suite.py`: Standard verification tests (Bare Mode compatible).
- `data/`: Sample datasets for knowledge base seeding.
