# 🧭 TalentScout – AI Hiring Assistant

TalentScout is an AI-powered Hiring Assistant chatbot that helps recruiters conduct initial candidate screenings efficiently.  
It collects candidate information, generates technical questions based on the candidate's tech stack, and stores responses for review.

**Live Demo:** [https://talentscoutapp-pgagi.streamlit.app/](https://talentscoutapp-pgagi.streamlit.app/)

## Installation

Use Python 3.9+ and [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
# Clone the repository
git clone https://github.com/Roopendra-M/talent_scout_app.git
cd talent_scout_app

# Create a virtual environment
python -m venv venv

# Activate the environment
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Set up Streamlit secrets:

```toml
# .streamlit/secrets.toml
HUGGINGFACE_API_TOKEN = "your_huggingface_token_here"
```

Initialize the database:

```bash
python -c "from db import init_db; init_db()"
```

Run the app:

```bash
streamlit run app.py
```

## Usage

```python
# Step 1: Candidate Information
# Enter your name, email, phone, experience, desired positions, location, and tech stack.
# Select preferred language and click "Save & Start Screening".

# Step 2: Technical Screening
# The chatbot generates 3-5 questions based on tech stack.
# Provide answers (open-ended or MCQ) and click "Save Answer" for each.
# Type 'bye' anytime to exit.

# Step 3: Wrap Up
# Review summary of responses.
# See candidate records in the demo table.
```

## Technical Details

- **Programming Language:** Python 3.x  
- **Libraries Used:** streamlit, requests, sqlite3  
- **LLM Used:** Hugging Face API (e.g., Microsoft DialoGPT-medium)  
- **Database:** SQLite (`candidates.db`)  

**Architecture:**  
- `db.py` – Handles candidate & answer storage  
- `app.py` – Streamlit app & session logic  
- `llm.py` – LLM question generation  
- `models.py` – Candidate & QAItem classes  
- `utils.py` – Validation & helper functions  
- `prompts.py` – Greetings and instructions  

## Prompt Design

- Collect candidate information in structured form.  
- Generate relevant technical questions from declared tech stack.  
- Use fallback questions if LLM API fails.

## Challenges & Solutions

| Challenge | Solution |
|-----------|---------|
| LLM API occasionally errors | Added fallback questions to continue screening |
| Sensitive API token exposure | Used `.streamlit/secrets.toml` and Git ignore rules |
| Session handling in Streamlit | Leveraged `st.session_state` to maintain candidate & question context |
| Candidate data storage | Implemented SQLite database via `db.py` for persistent storage |

## Future Enhancements

- Multilingual support for questions and responses  
- Sentiment analysis to gauge candidate confidence  
- Personalized feedback based on previous candidate history  
- Cloud deployment for scalability (AWS/GCP)  

## Contributing

Pull requests are welcome. For major changes, please open an issue first.  
Make sure to update tests and documentation as appropriate.

## License

This project is for educational purposes and PGAGI internship assignment use.
