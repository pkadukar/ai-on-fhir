import spacy
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text.lower())

    condition = None
    age = None

    # Try to extract AGE entity (spaCy sometimes misses this)
    for ent in doc.ents:
        if ent.label_ == "AGE":
            age = ent.text

    # Fallback to regex if spaCy doesn't catch age
    age_match = re.search(r"over (\d+)", text.lower())
    if age_match:
        age = f">{age_match.group(1)}"

    # Detect common medical conditions (expandable list)
    conditions = ["diabetes", "asthma", "hypertension"]
    for word in text.split():
        if word.lower() in conditions:
            condition = word.capitalize()

    return {
        "condition": condition,
        "age": age
    }

def simulate_fhir(parsed):
    # Use mock patients
    mock_data = [
        {"name": "Alice Smith", "age": 65, "condition": "Diabetes"},
        {"name": "Bob Johnson", "age": 52, "condition": "Hypertension"},
        {"name": "Charlie Lee", "age": 40, "condition": "Asthma"}
    ]

    results = []
    for patient in mock_data:
        if parsed["condition"] and parsed["condition"].lower() != patient["condition"].lower():
            continue
        if parsed["age"]:
            age_limit = int(parsed["age"].replace(">", ""))
            if patient["age"] <= age_limit:
                continue
        results.append({"resource": patient})

    return {
        "resourceType": "Bundle",
        "entry": results
    }
