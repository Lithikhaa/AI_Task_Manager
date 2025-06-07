# utils.py
from datetime import datetime, timedelta
import re

# This file intentionally does NOT import streamlit or call st.set_page_config
# to avoid violating Streamlit's page config order restriction

def load_nlp_models():
    try:
        import spacy
        return spacy.load("en_core_web_sm")
    except Exception:
        return None

def extract_tags(text):
    try:
        import spacy
        nlp = load_nlp_models()
        if not nlp:
            return ""
        doc = nlp(text)
        keywords = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]
        hashtags = set(re.findall(r"#\w+", text)) | set("#" + w for w in keywords[:3])
        return " ".join(hashtags)
    except:
        return ""

def parse_date_expressions(text):
    base = datetime.now()
    text = text.lower()
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
    ]

    for pat in date_patterns:
        match = re.search(pat, text)
        if match:
            try:
                if len(match.groups()) == 3:
                    g = list(map(int, match.groups()))
                    if g[0] > 31:  # Assume YYYY/MM/DD
                        return datetime(g[0], g[1], g[2])
                    elif g[2] > 31:  # DD/MM/YYYY
                        return datetime(g[2], g[1], g[0])
                    else:  # DD/MM/YY
                        return datetime(2000 + g[2], g[1], g[0])
            except:
                continue

    relative = {
        "today": 0, "tomorrow": 1,
        "day after tomorrow": 2,
        "next week": 7, "next month": 30
    }
    for key, offset in relative.items():
        if key in text:
            return base + timedelta(days=offset)

    for m in re.finditer(r'in (\d+) days?', text):
        return base + timedelta(days=int(m.group(1)))

    days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6}
    for name, num in days.items():
        if name in text:
            delta = (num - base.weekday() + 7) % 7
            return base + timedelta(days=delta)

    return base + timedelta(days=1)

def initialize_session_defaults():
    import streamlit as st
    defaults = {
        "task_added": False,
        "last_task": None,
        "edit_task_id": None,
        "task_input": "",
        "custom_category": "",
        "manual_date": datetime.today(),
        "manual_time": datetime.now().time(),
        "estimated_time": 0,
        "priority": "medium",
        "category": "autodetect"
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
