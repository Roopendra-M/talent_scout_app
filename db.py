import sqlite3
from pathlib import Path
from typing import List, Tuple

DB_PATH = Path("candidates.db")

def _connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = _connect()
    c = conn.cursor()
    
    # Ensure candidates table exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            years_experience REAL,
            desired_positions TEXT,
            current_location TEXT,
            tech_stack TEXT,
            language TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Ensure answers table exists (without sentiment first)
    c.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_email TEXT,
            q_number INTEGER,
            question TEXT,
            answer TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if 'sentiment' column exists; if not, add it
    c.execute("PRAGMA table_info(answers)")
    columns = [row[1] for row in c.fetchall()]
    if "sentiment" not in columns:
        c.execute("ALTER TABLE answers ADD COLUMN sentiment TEXT DEFAULT 'Neutral'")
    
    conn.commit()
    conn.close()

def add_candidate(cand) -> None:
    conn = _connect()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO candidates
        (name,email,phone,years_experience,desired_positions,current_location,tech_stack,language)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        cand['name'], cand['email'], cand['phone'], cand['years_experience'],
        ",".join(cand['desired_positions']), cand['current_location'], ",".join(cand['tech_stack']),
        cand['language']
    ))
    conn.commit()
    conn.close()

def save_answer(email: str, q_number: int, question: str, answer: str, sentiment: str = "Neutral"):
    conn = _connect()
    c = conn.cursor()
    c.execute("""
        INSERT INTO answers (candidate_email, q_number, question, answer, sentiment)
        VALUES (?,?,?,?,?)
    """, (email, q_number, question, answer, sentiment))
    conn.commit()
    conn.close()

def list_candidates() -> List[Tuple]:
    conn = _connect()
    c = conn.cursor()
    c.execute("""
        SELECT name,email,phone,years_experience,desired_positions,current_location,tech_stack,language,created_at
        FROM candidates
        ORDER BY created_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows
