# Lingo Enterprise API MVP Backend

This is an MVP backend in Python demonstrating enterprise language translation, grammar/style refinement, and audit capabilities.

The API implements five RESTful endpoints supporting enterprise integration requirements:
* **High Scale**: Core translation services (`/api/v1/translate`).
* **Partner Integrations**: Granular billing and usage tracking (`/api/v1/billing/usage`) and custom glossary alignment (`/api/v1/glossaries`).
* **Compliance & Security**: Strict GDPR-compliant routing (`/api/v1/translate` residency filters) and auditable data logs (`/api/v1/audit/logs`).
* **Writing Assistance**: Real-time writing style and tone optimization (`/api/v1/write-improve`).

---

## Getting Started

### 1. Prerequisites
Make sure you have Python 3.8+ installed.

### 2. Installation
Install the project dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Server
Start the local development server:
```bash
python main.py
```
Or run directly with uvicorn:
```bash
uvicorn main:app --reload
```
Once started, you can visit the interactive API documentation (Swagger UI) at:
* [Swagger UI Docs](http://127.0.0.1:8000/docs)
* [ReDoc](http://127.0.0.1:8000/redoc)

### 4. Running the Tests
To run the automated endpoint validation suite:
```bash
python test_api.py
```

---

## API Documentation

Below are the 5 RESTful API endpoints with concrete, realistic JSON request and response payloads.

### 1. Translate Text
* **Endpoint**: `POST /api/v1/translate`
* **Feature**: Core translation service with data residency options (`eu` vs `global`).

#### Request Payload
```json
{
  "text": [
    "Lingo is an AI-powered translation service."
  ],
  "target_lang": "DE",
  "source_lang": "EN",
  "glossary_id": "gloss_abc123",
  "data_residency": "eu"
}
```

#### Response Payload (200 OK)
```json
{
  "translations": [
    {
      "detected_source_language": "EN",
      "text": "Lingo ist ein KI-gestützter Übersetzungsdienst."
    }
  ],
  "data_residency_routed": "eu",
  "billed_characters": 43
}
```

---

### 2. Improve Writing Style (Lingo Write)
* **Endpoint**: `POST /api/v1/write-improve`
* **Feature**: Real-time writing style and tone optimization.

#### Request Payload
```json
{
  "text": "I is writing this email to let you know that the API is ready for test.",
  "target_lang": "EN",
  "style": "business",
  "tone": "confident"
}
```

#### Response Payload (200 OK)
```json
{
  "improved_text": "I am writing this email to inform you that the API is ready for testing.",
  "suggestions": [
    {
      "original": "I is writing",
      "replaced_with": "I am writing",
      "reason": "Subject-verb agreement correction"
    },
    {
      "original": "let you know that",
      "replaced_with": "inform you that",
      "reason": "Business tone enhancement"
    },
    {
      "original": "ready for test",
      "replaced_with": "ready for testing",
      "reason": "Idiomatic phrasing"
    }
  ],
  "style_applied": "business",
  "tone_applied": "confident"
}
```

---

### 3. Create Glossary
* **Endpoint**: `POST /api/v1/glossaries`
* **Feature**: Custom terminology dictionaries for translation consistency.

#### Request Payload
```json
{
  "name": "Tech Terminology Glossary",
  "source_lang": "EN",
  "target_lang": "FR",
  "entries": [
    {
      "source": "API Gateway",
      "target": "Passerelle API"
    },
    {
      "source": "data residency",
      "target": "résidence des données"
    }
  ]
}
```

#### Response Payload (200 OK)
```json
{
  "glossary_id": "gloss_tech_987",
  "name": "Tech Terminology Glossary",
  "source_lang": "EN",
  "target_lang": "FR",
  "entry_count": 2,
  "created_at": "2026-06-10T12:00:00Z",
  "status": "ready"
}
```

---

### 4. Fetch Granular Billing & Usage
* **Endpoint**: `GET /api/v1/billing/usage`
* **Feature**: Hourly/daily billing usage metrics for client subscriptions.
* **Headers**: `Authorization: Bearer api_key_123`
* **Query Parameters**:
  * `start_date`: `2026-06-01`
  * `end_date`: `2026-06-10`

#### Response Payload (200 OK)
```json
{
  "client_id": "client_enterprise_acme",
  "billing_period": {
    "start": "2026-06-01T00:00:00Z",
    "end": "2026-06-10T23:59:59Z"
  },
  "usage_summary": {
    "total_translation_characters": 12543000,
    "total_writing_improved_characters": 3400000,
    "total_api_calls": 84500
  },
  "cost_breakdown_usd": {
    "translation_cost": 250.86,
    "writing_cost": 68.0,
    "base_subscription": 150.0,
    "total_due": 468.86
  },
  "currency": "USD"
}
```

#### Response Payload (401 Unauthorized - invalid or missing header)
```json
{
  "detail": "Invalid or missing API credentials."
}
```

---

### 5. Query Audit Logs (GDPR Residency Compliance)
* **Endpoint**: `POST /api/v1/audit/logs`
* **Feature**: Verification audit trail ensuring data residency compliance.

#### Request Payload
```json
{
  "client_id": "client_enterprise_acme",
  "compliance_framework": "GDPR",
  "limit": 10,
  "filter": {
    "residency": "eu",
    "event_type": "translation_processing"
  }
}
```

#### Response Payload (200 OK)
```json
{
  "audit_id": "audit_log_2026_06_10",
  "compliance_framework": "GDPR",
  "verified_residency": "eu",
  "logs": [
    {
      "timestamp": "2026-06-10T12:30:15Z",
      "event_id": "evt_908123",
      "action": "translate_request",
      "server_location": "Frankfurt, Germany (AWS eu-central-1)",
      "data_deleted_at": "2026-06-10T12:30:16Z",
      "gdpr_compliant": true
    },
    {
      "timestamp": "2026-06-10T12:31:00Z",
      "event_id": "evt_908124",
      "action": "translate_request",
      "server_location": "Frankfurt, Germany (AWS eu-central-1)",
      "data_deleted_at": "2026-06-10T12:31:01Z",
      "gdpr_compliant": true
    }
  ]
}
```
