# backend/test_app.py

from app import extract_conditions, extract_age, build_fhir_query

def test_extract_conditions():
    assert extract_conditions("Find diabetic patients") == ['diabetic']
    assert extract_conditions("Patients with asthma and cancer") == ['asthma', 'cancer']
    assert extract_conditions("No known conditions") == []

def test_extract_age():
    assert extract_age("over 50") == ('gt', 50)
    assert extract_age("under 30") == ('lt', 30)
    assert extract_age("above 60") == ('gt', 60)
    assert extract_age("less than 45") == ('lt', 45)
    assert extract_age("no age mentioned") == (None, None)

def test_build_fhir_query():
    query = build_fhir_query(['asthma'], 'lt', 30)
    expected = {
        "resourceType": "Patient",
        "filters": {
            "condition": ['asthma'],
            "age": {
                "operator": 'lt',
                "value": 30
            }
        }
    }
    assert query == expected
