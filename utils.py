import re

EXIT_KEYWORDS = ["bye", "exit", "quit"]

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_phone(phone):
    return re.match(r"^\+?\d{10,15}$", phone)

def validate_years(years):
    try:
        return float(years) >= 0
    except:
        return False

def sanitize_list(text):
    return [x.strip() for x in text.split(",") if x.strip()]
