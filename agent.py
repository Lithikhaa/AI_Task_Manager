# agent.py
import re
import json
import pickle
from datetime import datetime, timedelta
import spacy

from utils import load_nlp_models, extract_tags, parse_date_expressions

class AdvancedTaskAgent:
    def __init__(self):
        self.nlp = load_nlp_models()
        self.categories = {
            "shopping": ["buy", "purchase", "order", "groceries", "shop"],
            "work": ["report", "meeting", "project", "email"],
            "office": ["submit", "follow-up", "document"],
            "interview": ["interview", "resume", "job"],
            "personal": ["call", "movie", "relax"],
            "health": ["doctor", "medicine", "gym"],
            "finance": ["bill", "pay", "salary"],
            "learning": ["study", "learn", "course"],
            "travel": ["travel", "trip", "ticket"],
            "home": ["clean", "repair", "cook"]
        }

    def extract_entities(self, text):
        if not self.nlp:
            return []
        doc = self.nlp(text)
        return [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'TIME']]

    def estimate_duration(self, text, category):
        base_durations = {
            "shopping": 45, "work": 90, "office": 30, "interview": 60,
            "personal": 30, "health": 45, "finance": 30,
            "learning": 60, "travel": 120, "home": 60, "other": 45
        }
        base = base_durations.get(category, 45)
        multiplier = 1.0
        text_lower = text.lower()

        for keyword, factor in {
            "quick": 0.3, "fast": 0.3, "brief": 0.4,
            "standard": 1.0, "complete": 1.7, "deep": 2.0
        }.items():
            if keyword in text_lower:
                multiplier = factor
                break

        for keyword, mins in {
            "email": 15, "call": 20, "meeting": 60,
            "report": 120, "project": 180, "shopping": 60,
            "study": 90, "doctor": 60
        }.items():
            if keyword in text_lower:
                return max(int(mins * multiplier), 10)

        for pattern in [r'(\d+)\s*(minutes?|mins?)', r'(\d+)\s*(hours?|hrs?)']:
            match = re.search(pattern, text_lower)
            if match:
                val = int(match.group(1))
                return max(val * (60 if 'hour' in match.group(2) else 1), 10)

        return max(int(base * multiplier), 10)

    def generate_ai_suggestions(self, text, category):
        text = text.lower()
        suggest = {
            "work": ["Prepare agenda", "Set reminders"],
            "shopping": ["Make a list", "Compare prices"],
            "health": ["Book appointment", "Bring ID"],
            "finance": ["Check balance", "Keep docs ready"]
        }
        suggestions = suggest.get(category, [])
        if len(text.split()) > 8:
            suggestions.append("Break into subtasks")
        return suggestions[:3]

    def smart_categorize(self, text):
        text_lower = text.lower()
        try:
            with open('models/task_categorizer_model.pkl', 'rb') as f:
                model = pickle.load(f)
            with open('models/tfidf_vectorizer.pkl', 'rb') as f:
                vectorizer = pickle.load(f)
            features = vectorizer.transform([re.sub(r'[^a-zA-Z\s]', '', text_lower)])
            return model.predict(features)[0]
        except:
            for category, keywords in self.categories.items():
                if any(word in text_lower for word in keywords):
                    return category
            return "personal"

    def parse_advanced_natural_language(self, input_str, forced_category=None, forced_priority=None):
        due_time = re.search(r'(\d{1,2})(:\d{2})?\s*(am|pm)', input_str, re.I)
        due_date = parse_date_expressions(input_str)

        if due_time:
            hour = int(due_time.group(1)) % 12
            minute = int(due_time.group(2)[1:]) if due_time.group(2) else 0
            if due_time.group(3).lower() == 'pm' and hour != 12:
                hour += 12
            due_date = due_date.replace(hour=hour, minute=minute)
        else:
            due_date = due_date.replace(hour=23, minute=59)

        category = forced_category or self.smart_categorize(input_str)
        duration = self.estimate_duration(input_str, category)
        suggestions = self.generate_ai_suggestions(input_str, category)
        entities = self.extract_entities(input_str)

        priority = forced_priority or (
            "high" if any(x in input_str.lower() for x in ["urgent", "asap"]) else
            "medium" if any(x in input_str.lower() for x in ["important", "priority"]) else
            "low"
        )

        return {
            "task_name": input_str.strip(),
            "category": category,
            "priority": priority,
            "due_date": due_date.strftime('%Y-%m-%d %H:%M:%S'),
            "status": "pending",
            "tags": extract_tags(input_str),
            "estimated_duration": duration,
            "ai_suggestions": json.dumps(suggestions),
            "context_keywords": " ".join(entities)
        }
