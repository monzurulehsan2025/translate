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
    
    if method == "POST":
        response = client.post(path, json=payload, headers=headers)
    elif method == "GET":
        response = client.get(path, headers=headers)
    else:
        raise ValueError(f"Unsupported method {method}")
        
    print(f"Response Status Code: {response.status_code}")
    if "X-Cache" in response.headers:
        print(f"X-Cache Header: {response.headers['X-Cache']}")
        
    try:
        response_json = response.json()
        print(f"Response Payload:\n{json.dumps(response_json, indent=2)}")
    except Exception as e:
        print(f"Raw Response Content: {response.text}")
        response_json = None
        
    print("=" * 70 + "\n")
    return response, response_json

def test_caching_behavior():
    print("=" * 70)
    print("TESTING CACHING BEHAVIOR")
    translate_payload = {
        "text": ["Lingo caching test sentence."],
        "target_lang": "FR",
        "data_residency": "eu"
    }

    # Call 1: Expect Cache MISS
    r1 = client.post("/api/v1/translate", json=translate_payload)
    print(f"Call 1 - Status: {r1.status_code} | X-Cache Header: {r1.headers.get('X-Cache')}")
    assert r1.status_code == 200
    assert r1.headers.get("X-Cache") == "MISS", "First call should miss cache"

    # Call 2: Expect Cache HIT
    r2 = client.post("/api/v1/translate", json=translate_payload)
    print(f"Call 2 - Status: {r2.status_code} | X-Cache Header: {r2.headers.get('X-Cache')}")
    assert r2.status_code == 200
    assert r2.headers.get("X-Cache") == "HIT", "Second call should hit cache"

    print("Caching behavior verified successfully!")
    print("=" * 70 + "\n")

def test_rate_limiting_behavior():
    print("=" * 70)
    print("TESTING RATE LIMITING (High Load Protection)")
    
    # We will trigger the writing improver endpoint in a loop.
    # The writing improver has a capacity of 20.
    write_payload = {
        "text": "Lingo write load test",
        "target_lang": "EN",
        "style": "casual",
        "tone": "friendly"
    }
    
    success_count = 0
    blocked_count = 0
    
    # Fire 30 requests rapidly to exceed the capacity of 20
    for i in range(30):
        r = client.post("/api/v1/write-improve", json=write_payload)
        if r.status_code == 200:
            success_count += 1
        elif r.status_code == 429:
            blocked_count += 1
            if blocked_count == 1:
                # Log details of the first blocked call
                print(f"First rate-limited block hit at loop iteration {i+1}:")
                print(f"Status Code: {r.status_code}")
                print(f"Response Headers: {dict(r.headers)}")
                print(f"Response Payload: {r.json()}")
                assert "Retry-After" in r.headers
                assert r.json()["detail"] == "Too Many Requests. Rate limit exceeded. Retry after 1 second."

    print(f"Rate Limiting Simulation: Succeeded={success_count}, Blocked (429)={blocked_count}")
    assert blocked_count > 0, "Rate limiter did not block requests. Capacity is 20, we sent 30."
    print("Rate limiting behavior verified successfully!")
    print("=" * 70 + "\n")

def run_all_tests():
    print("Starting Scale Verification Test Suite...\n")
    
    # Basic functional tests (same checks as original suite)
    translate_payload = {
        "text": ["Lingo is an AI-powered translation service."],
        "target_lang": "DE",
        "source_lang": "EN",
        "glossary_id": "gloss_abc123",
        "data_residency": "eu"
    }
    r1, _ = test_endpoint("1. Text Translation (residency=eu, target=DE)", "POST", "/api/v1/translate", translate_payload)
    assert r1.status_code == 200, "Translate endpoint failed"

    write_payload = {
        "text": "I is writing this email to let you know that the API is ready for test.",
        "target_lang": "EN",
        "style": "business",
        "tone": "confident"
    }
    r2, _ = test_endpoint("2. Writing Improvement (Lingo Write style=business)", "POST", "/api/v1/write-improve", write_payload)
    assert r2.status_code == 200, "Write-improve endpoint failed"

    glossary_payload = {
        "name": "Tech Terminology Glossary",
        "source_lang": "EN",
        "target_lang": "FR",
        "entries": [
            {"source": "API Gateway", "target": "Passerelle API"},
            {"source": "data residency", "target": "résidence des données"}
        ]
    }
    r3, _ = test_endpoint("3. Create Glossary", "POST", "/api/v1/glossaries", glossary_payload)
    assert r3.status_code == 200, "Glossaries endpoint failed"

    billing_headers = {
        "Authorization": "Bearer api_key_123"
    }
    r4, _ = test_endpoint("4. Granular Billing & Usage (Authorized)", "GET", "/api/v1/billing/usage?start_date=2026-06-01&end_date=2026-06-10", headers=billing_headers)
    assert r4.status_code == 200, "Billing endpoint failed"

    r4b, _ = test_endpoint("4b. Granular Billing & Usage (Unauthorized)", "GET", "/api/v1/billing/usage?start_date=2026-06-01&end_date=2026-06-10")
    assert r4b.status_code == 401, "Billing authentication security check failed"

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
    
    # Scale feature tests
    test_caching_behavior()
    test_rate_limiting_behavior()
    
    print("All scale verification tests passed successfully!")

if __name__ == "__main__":
    run_all_tests()
