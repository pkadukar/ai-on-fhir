from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from datetime import timedelta
import re
import spacy
from flask_cors import CORS

# === App Configuration ===
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests (frontend/backend communication)

# Load spaCy model for NLP
nlp = spacy.load("en_core_web_sm")

# Flask config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # Local database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret"  # Replace in production!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

# Initializing extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# === User Model ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# === One-time DB Setup Hook ===
init_done = False

@app.before_request
def startup():
    global init_done
    if not init_done:
        db.create_all()
        print("Initialized database.")
        init_done = True

# === NLP Extraction Helpers ===

def extract_conditions(text):
    """Extracts known medical conditions from user input."""
    synonym_map = {
        "diabetes": "diabetic",
        "diabetic": "diabetic",
        "high blood pressure": "hypertension",
        "hypertension": "hypertension",
        "covid": "covid",
        "covid-19": "covid",
        "coronavirus": "covid",
        "asthma": "asthma",
        "cancer": "cancer"
    }

    found = set()
    text = text.lower()
    for key_phrase, canonical in synonym_map.items():
        if key_phrase in text:
            found.add(canonical)

    return list(found)

def extract_age(text):
    """Parses age filter like 'over 60' or 'under 40'."""
    age, age_op = None, None
    match = re.search(r'(over|under|above|below|greater than|less than)?\s*(\d{1,3})', text.lower())
    if match:
        op_map = {
            'over': 'gt',
            'above': 'gt',
            'greater than': 'gt',
            'under': 'lt',
            'below': 'lt',
            'less than': 'lt'
        }
        age_op = match.group(1)
        age = int(match.group(2))
        if age_op:
            age_op = op_map.get(age_op, None)
    return age_op, age

def extract_gender(text):
    """Detects gender filters (male, female, other)."""
    text = text.lower()
    if 'female' in text:
        return 'female'
    elif 'male' in text:
        return 'male'
    elif 'other' in text:
        return 'other'
    return None

def extract_medications(text):
    """Looks for known medications in the query."""
    meds = ['aspirin', 'ibuprofen', 'metformin', 'lisinopril']
    return [med for med in meds if med in text.lower()]

def extract_visit_dates(text):
    """Placeholder for future use: visit date extraction."""
    return None

def build_fhir_query(conditions, age_op, age, gender=None, medications=None, visit_dates=None):
    """Constructs a simulated FHIR filter response."""
    fhir_query = {
        "resourceType": "Patient",
        "filters": {}
    }
    if conditions:
        fhir_query["filters"]["condition"] = conditions
    if age_op and age:
        fhir_query["filters"]["age"] = {
            "operator": age_op,
            "value": age
        }
    if gender:
        fhir_query["filters"]["gender"] = gender
    if medications:
        fhir_query["filters"]["medications"] = medications
    if visit_dates:
        fhir_query["filters"]["visit_dates"] = visit_dates
    return fhir_query

# === Auth Routes ===

@app.route('/signup', methods=['POST'])
def signup():
    """Registers a new user with hashed password."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Logs in an existing user and returns JWT token."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

# === Query Endpoint ===

@app.route('/query', methods=['POST'])
@jwt_required()
def query():
    """Main NLP endpoint that parses a natural query and returns matched patients."""
    current_user = get_jwt_identity()
    data = request.get_json()

    if not data or "query" not in data or not isinstance(data["query"], str) or not data["query"].strip():
        return jsonify({"error": "'query' cannot be empty"}), 400

    user_query = data["query"]

    # Applying NLP extraction
    conditions = extract_conditions(user_query)
    age_op, age = extract_age(user_query)
    gender = extract_gender(user_query)
    medications = extract_medications(user_query)
    visit_dates = extract_visit_dates(user_query)

    # Building filter metadata
    fhir_query = build_fhir_query(conditions, age_op, age, gender, medications, visit_dates)

    # === Simulated Patient Records ===
    mock_data = [
        {"name": "Alice Smith", "age": 65, "condition": "diabetic", "gender": "female"},
        {"name": "Bob Johnson", "age": 52, "condition": "hypertension", "gender": "male"},
        {"name": "Charlie Lee", "age": 40, "condition": "asthma", "gender": "male"},
        {"name": "Dana White", "age": 60, "condition": "hypertension", "gender": "female"},
        {"name": "Eva Kumar", "age": 35, "condition": "asthma", "gender": "female"},
        {"name": "Frank Wu", "age": 70, "condition": "covid", "gender": "male"},
        {"name": "Grace Adams", "age": 55, "condition": "diabetic", "gender": "female", "medications": ["aspirin"]},
        {"name": "Hassan Ali", "age": 58, "condition": "diabetic", "gender": "male", "medications": ["metformin"]}
    ]

    # === Filtering Logic ===
    results = []
    for patient in mock_data:
        match = True

        if conditions and not any(cond.lower() in patient["condition"].lower() for cond in conditions):
            match = False

        if age_op and age is not None:
            if (age_op == "gt" and patient["age"] <= age) or (age_op == "lt" and patient["age"] >= age):
                match = False

        if gender and patient.get("gender", "").lower() != gender.lower():
            match = False

        if medications:
            patient_meds = patient.get("medications", [])
            if not any(med.lower() in [m.lower() for m in patient_meds] for med in medications):
                match = False

        if match:
            results.append({"resource": patient})

    # Final response
    response = {
        "resourceType": "Patient",
        "filters": fhir_query["filters"],
        "entry": results if results else []
    }

    # Logging
    print(f"User: {current_user}")
    print("Query received:", user_query)
    print("Extracted filters:", fhir_query["filters"])
    if not results:
        print("No patients matched the query.")
    else:
        print(f"Found {len(results)} matching patients.")

    return jsonify(response), 200

# === Protected Test Route ===

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Test route to verify token-based access."""
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# === Run App ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
