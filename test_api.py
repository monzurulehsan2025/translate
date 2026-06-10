import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoint(name: str, method: str, path: str, payload: dict = None, headers: dict = None):
    print("=" * 70)
    print(f"TESTING ENDPOINT: {name}")
    print(f"Method: {method} | Path: {path}")
    if headers:
        print(f"Headers: {json.dumps(headers, indent=2)}")
    if payload:
        print(f"Request Payload:\n{json.dumps(payload, indent=2)}")
    
    # Execute request
    if method == "POST":
        response = client.post(path, json=payload, headers=headers)
    elif method == "GET":
        response = client.get(path, headers=headers)
    else:
        raise ValueError(f"Unsupported method {method}")
        
    print(f"Response Status Code: {response.status_code}")
    try:
        response_json = response.json()
        print(f"Response Payload:\n{json.dumps(response_json, indent=2)}")
    except Exception as e:
        print(f"Raw Response Content: {response.text}")
        response_json = None
        
    print("=" * 70 + "\n")
    return response, response_json

def run_all_tests():
    print("Starting API Endpoint Verification Suite...\n")
    
    # 1. POST /api/v1/translate
    translate_payload = {
        "text": ["Lingo is an AI-powered translation service."],
        "target_lang": "DE",
        "source_lang": "EN",
        "glossary_id": "gloss_abc123",
        "data_residency": "eu"
    }
    r1, _ = test_endpoint("1. Text Translation (residency=eu, target=DE)", "POST", "/api/v1/translate", translate_payload)
    assert r1.status_code == 200, "Translate endpoint failed"

    # 2. POST /api/v1/write-improve
    write_payload = {
        "text": "I is writing this email to let you know that the API is ready for test.",
        "target_lang": "EN",
        "style": "business",
        "tone": "confident"
    }
    r2, _ = test_endpoint("2. Writing Improvement (Lingo Write style=business)", "POST", "/api/v1/write-improve", write_payload)
    assert r2.status_code == 200, "Write-improve endpoint failed"

    # 3. POST /api/v1/glossaries
    glossary_payload = {
        "name": "Tech Terminology Glossary",
        "source_lang": "EN",
        "target_lang": "FR",
        "entries": [
            {"source": "API Gateway", "target": "Passerelle API"},
            {"source": "data residency", "target": "résidence des données"}
        ]
    }
    r3, _ = test_endpoint("3. Create Glossary (for terminology synchronization)", "POST", "/api/v1/glossaries", glossary_payload)
    assert r3.status_code == 200, "Glossaries endpoint failed"

    # 4. GET /api/v1/billing/usage
    billing_headers = {
        "Authorization": "Bearer api_key_123"
    }
    r4, _ = test_endpoint("4. Granular Billing & Usage (Authorized API access)", "GET", "/api/v1/billing/usage?start_date=2026-06-01&end_date=2026-06-10", headers=billing_headers)
    assert r4.status_code == 200, "Billing endpoint failed"

    # 4b. GET /api/v1/billing/usage (Unauthorized check)
    r4b, _ = test_endpoint("4b. Granular Billing & Usage (Unauthorized request)", "GET", "/api/v1/billing/usage?start_date=2026-06-01&end_date=2026-06-10")
    assert r4b.status_code == 401, "Billing authentication security check failed"

    # 5. POST /api/v1/audit/logs
    audit_payload = {
        "client_id": "client_enterprise_acme",
        "compliance_framework": "GDPR",
        "limit": 10,
        "filter": {
            "residency": "eu",
            "event_type": "translation_processing"
        }
    }
    r5, _ = test_endpoint("5. Compliance and Data Residency Audit Logs (GDPR logs)", "POST", "/api/v1/audit/logs", audit_payload)
    assert r5.status_code == 200, "Audit logs endpoint failed"
    
    print("All verification tests passed successfully!")

if __name__ == "__main__":
    run_all_tests()
