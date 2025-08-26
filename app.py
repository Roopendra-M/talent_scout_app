import streamlit as st
from db import init_db, add_candidate, list_candidates, save_answer
from models import Candidate, QAItem
from utils import (
    validate_email, validate_phone, validate_years, sanitize_list,
    EXIT_KEYWORDS
)
from llm import generate_questions, analyze_sentiment
from prompts import GREETING

# ---------- App setup ----------
st.set_page_config(page_title="TalentScout – Hiring Assistant", layout="wide")
st.title("🧭 TalentScout – AI Hiring Assistant")

# Custom styling
st.markdown("""
<style>
div.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #1e40af;
}
</style>
""", unsafe_allow_html=True)

# greet + purpose
with st.expander("What is this?", expanded=True):
    st.markdown(GREETING)

# init db once
init_db()

# ---------- Session state ----------
if "stage" not in st.session_state:
    st.session_state.stage = "collect"
if "candidate" not in st.session_state:
    st.session_state.candidate = None
if "questions" not in st.session_state:
    st.session_state.questions = []
if "language" not in st.session_state:
    st.session_state.language = "English"

# ---------- Step 1: Collect candidate info ----------
if st.session_state.stage == "collect":
    st.header("Step 1 · Candidate Information")

    cols = st.columns(2)
    with cols[0]:
        full_name = st.text_input("Full Name*", placeholder="e.g., Priya Sharma")
        email = st.text_input("Email*", placeholder="name@example.com")
        phone = st.text_input("Phone*", placeholder="+91XXXXXXXXXX")
        years_exp = st.text_input("Years of Experience*", placeholder="e.g., 3")
    with cols[1]:
        desired_positions = st.text_input("Desired Position(s)*", placeholder="e.g., Python Developer, Data Scientist")
        current_location = st.text_input("Current Location*", placeholder="e.g., Bengaluru, IN")
        tech_stack = st.text_area(
            "Tech Stack* (comma-separated)",
            placeholder="e.g., Python, Django, SQL, Pandas, Docker"
        )
        st.session_state.language = st.selectbox("Preferred Language", ["English", "Hindi", "Other"])

    submitted = st.button("Save & Start Screening", width='stretch')
    if submitted:
        # validations
        if not full_name or not email or not phone or not years_exp or not desired_positions or not current_location or not tech_stack:
            st.error("⚠️ Please fill all required fields (*)")
        elif not validate_email(email):
            st.error("⚠️ Invalid email format.")
        elif not validate_phone(phone):
            st.error("⚠️ Invalid phone number.")
        elif not validate_years(years_exp):
            st.error("⚠️ Years of experience must be a number >= 0.")
        else:
            skills = sanitize_list(tech_stack)
            positions = sanitize_list(desired_positions)

            cand = Candidate(
                name=full_name.strip(),
                email=email.strip(),
                phone=phone.strip(),
                years_experience=float(years_exp),
                desired_positions=positions,
                current_location=current_location.strip(),
                tech_stack=skills,
                language=st.session_state.language
            )
            add_candidate(cand.__dict__)
            st.session_state.candidate = cand
            st.session_state.stage = "questions"
            st.rerun()

# ---------- Step 2: Generate + ask questions ----------
elif st.session_state.stage == "questions":
    st.header("Step 2 · Technical Screening")
    cand = st.session_state.candidate

    # Exit keyword listener
    user_exit = st.text_input("Type message (optional):", placeholder="Type 'bye' to end anytime")
    if user_exit and user_exit.strip().lower() in EXIT_KEYWORDS:
        st.info("👋 Ending conversation as requested. Thanks for your time!")
        st.session_state.stage = "done"
        st.rerun()

    # Generate questions once
    if not st.session_state.questions:
        with st.spinner("🤖 Generating tailored questions from your tech stack..."):
            qs = generate_questions(
                techs=cand.tech_stack,
                language=cand.language,
                n_min=3,
                n_max=5
            )
            st.session_state.questions = qs

    # Render questions
    for idx, q in enumerate(st.session_state.questions, start=1):
        st.markdown(f"**Q{idx}. {q.question}**")
        st.progress(idx / len(st.session_state.questions))

        if q.kind == "MCQ" and q.options:
            choice = st.radio("Choose one", q.options, key=f"mcq_{idx}")
            if st.button(f"Save Answer Q{idx}", key=f"save_{idx}"):
                sentiment = analyze_sentiment(choice)
                save_answer(cand.email, idx, q.question, choice, sentiment)
                st.success(f"✅ Saved. (Sentiment: {sentiment})")
                st.info(f"🤖 Bot: Thanks {cand.name}, I’ve recorded your answer.")
        else:
            ans = st.text_area("Your answer", key=f"open_{idx}", height=120)
            if st.button(f"Save Answer Q{idx}", key=f"save_{idx}"):
                sentiment = analyze_sentiment(ans)
                save_answer(cand.email, idx, q.question, ans, sentiment)
                st.success(f"✅ Saved. (Sentiment: {sentiment})")
                st.info(f"🤖 Bot: Thanks {cand.name}, I’ve recorded your answer.")

    if st.button("Finish Interview", type="primary", width='stretch'):
        st.session_state.stage = "done"
        st.rerun()

# ---------- Step 3: Wrap up ----------
elif st.session_state.stage == "done":
    st.subheader("Step 3 · Thank You & Next Steps 🎉")

    cand = st.session_state.candidate
    if cand:
        st.success(f"✅ Thank you, {cand.name}, for completing the screening!")
        st.markdown(f"""
        **Summary:**
        - Email: {cand.email}
        - Phone: {cand.phone}
        - Experience: {cand.years_experience} years
        - Roles: {', '.join(cand.desired_positions)}
        - Location: {cand.current_location}
        - Tech Stack: {', '.join(cand.tech_stack)}
        - Language: {cand.language}
        """)

    st.info("Our team will review your responses and contact you with next steps. 💼")
    st.divider()
    st.subheader("📋 Candidate Records (Demo Only)")
    rows = list_candidates()
    st.dataframe(rows, width='stretch')
