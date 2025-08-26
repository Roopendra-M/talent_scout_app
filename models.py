from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Candidate:
    name: str
    email: str
    phone: str
    years_experience: float
    desired_positions: List[str]
    current_location: str
    tech_stack: List[str]
    language: str

@dataclass
class QAItem:
    question: str
    kind: str = "Open"
    options: Optional[List[str]] = None
