from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Lingo Enterprise API MVP",
    description="MVP API platform backend demonstrating Translation, Writing Improvement, Glossaries, Billing, and GDPR Data Residency Audit features.",
    version="1.0.0"
)

# =====================================================================
# 1. Translate Endpoint
# =====================================================================

class TranslateRequest(BaseModel):
    text: List[str] = Field(..., description="List of strings to translate.")
    target_lang: str = Field(..., description="ISO 639-1 language code (e.g., 'DE', 'FR', 'ES').")
    source_lang: Optional[str] = Field(None, description="Source language code. Auto-detected if not provided.")
    glossary_id: Optional[str] = Field(None, description="Optional ID of custom glossary to apply.")
    data_residency: str = Field("global", description="Residency rule for data processing: 'eu' or 'global'.")

class TranslationResult(BaseModel):
    detected_source_language: str
    text: str

class TranslateResponse(BaseModel):
    translations: List[TranslationResult]
    data_residency_routed: str
    billed_characters: int

@app.post("/api/v1/translate", response_model=TranslateResponse, tags=["Translation"])
async def translate(request: TranslateRequest):
    # Data Residency Validation
    if request.data_residency not in ["eu", "global"]:
        raise HTTPException(status_code=400, detail="Data residency must be 'eu' or 'global'.")

    # Target Language Validation
    supported_langs = ["DE", "FR", "ES", "EN", "IT", "JA"]
    if request.target_lang.upper() not in supported_langs:
        raise HTTPException(status_code=400, detail=f"Unsupported target language. Supported: {supported_langs}")

    # Simulated translation logic (hardcoded but responsive to input)
    translations = []
    total_chars = 0
    for t in request.text:
        total_chars += len(t)
        # Default translation simulation if text matches our demo text
        if "Lingo is an AI-powered translation service" in t:
            if request.target_lang.upper() == "DE":
                translated_text = "Lingo ist ein KI-gestützter Übersetzungsdienst."
            elif request.target_lang.upper() == "FR":
                translated_text = "Lingo est un service de traduction basé sur l'IA."
            else:
                translated_text = f"[Mock translation to {request.target_lang.upper()}] {t}"
        else:
            translated_text = f"[Mock translation to {request.target_lang.upper()}] {t}"
            
        translations.append(TranslationResult(
            detected_source_language=request.source_lang or "EN",
            text=translated_text
        ))

    return TranslateResponse(
        translations=translations,
        data_residency_routed=request.data_residency,
        billed_characters=total_chars
    )


# =====================================================================
# 2. Write-Improve Endpoint
# =====================================================================

class WriteImproveRequest(BaseModel):
    text: str = Field(..., description="Text to improve.")
    target_lang: str = Field("EN", description="Language of text to improve.")
    style: str = Field("business", description="Writing style preference: 'business', 'casual', 'academic'.")
    tone: str = Field("confident", description="Tone preference: 'confident', 'friendly', 'diplomatic'.")

class Suggestion(BaseModel):
    original: str
    replaced_with: str
    reason: str

class WriteImproveResponse(BaseModel):
    improved_text: str
    suggestions: List[Suggestion]
    style_applied: str
    tone_applied: str

@app.post("/api/v1/write-improve", response_model=WriteImproveResponse, tags=["Writing Improvement"])
async def write_improve(request: WriteImproveRequest):
    # Tone and Style Validation
    if request.style not in ["business", "casual", "academic"]:
        raise HTTPException(status_code=400, detail="Style must be 'business', 'casual', or 'academic'.")
    if request.tone not in ["confident", "friendly", "diplomatic"]:
        raise HTTPException(status_code=400, detail="Tone must be 'confident', 'friendly', or 'diplomatic'.")

    # Return high-fidelity hardcoded translation improvement data
    # Designed to respond to the specific example sentence in our demo suite
    if "I is writing this email" in request.text:
        improved = "I am writing this email to inform you that the API is ready for testing."
        suggestions = [
            Suggestion(original="I is writing", replaced_with="I am writing", reason="Subject-verb agreement correction"),
            Suggestion(original="let you know that", replaced_with="inform you that", reason="Business tone enhancement"),
            Suggestion(original="ready for test", replaced_with="ready for testing", reason="Idiomatic phrasing")
        ]
    else:
        improved = f"[Enhanced Style: {request.style}, Tone: {request.tone}] {request.text}"
        suggestions = [
            Suggestion(original=request.text[:10], replaced_with=f"[Enhanced {request.style}]", reason="Style refinement")
        ]

    return WriteImproveResponse(
        improved_text=improved,
        suggestions=suggestions,
        style_applied=request.style,
        tone_applied=request.tone
    )


# =====================================================================
# 3. Glossaries Endpoint
# =====================================================================

class GlossaryEntry(BaseModel):
    source: str
    target: str

class GlossaryCreateRequest(BaseModel):
    name: str = Field(..., description="Descriptive name for the glossary.")
    source_lang: str = Field(..., description="Source language ISO code.")
    target_lang: str = Field(..., description="Target language ISO code.")
    entries: List[GlossaryEntry] = Field(..., description="List of term pairs.")

class GlossaryCreateResponse(BaseModel):
    glossary_id: str
    name: str
    source_lang: str
    target_lang: str
    entry_count: int
    created_at: str
    status: str

@app.post("/api/v1/glossaries", response_model=GlossaryCreateResponse, tags=["Glossary Management"])
async def create_glossary(request: GlossaryCreateRequest):
    if len(request.entries) == 0:
        raise HTTPException(status_code=400, detail="At least one glossary entry is required.")

    return GlossaryCreateResponse(
        glossary_id="gloss_tech_987",
        name=request.name,
        source_lang=request.source_lang.upper(),
        target_lang=request.target_lang.upper(),
        entry_count=len(request.entries),
        created_at="2026-06-10T12:00:00Z",
        status="ready"
    )


# =====================================================================
# 4. Billing/Usage Endpoint
# =====================================================================

class BillingPeriod(BaseModel):
    start: str
    end: str

class UsageSummary(BaseModel):
    total_translation_characters: int
    total_writing_improved_characters: int
    total_api_calls: int

class CostBreakdown(BaseModel):
    translation_cost: float
    writing_cost: float
    base_subscription: float
    total_due: float

class BillingResponse(BaseModel):
    client_id: str
    billing_period: BillingPeriod
    usage_summary: UsageSummary
    cost_breakdown_usd: CostBreakdown
    currency: str

@app.get("/api/v1/billing/usage", response_model=BillingResponse, tags=["Billing & Usage"])
async def get_billing_usage(
    start_date: str = Query("2026-06-01", description="Billing range start date (YYYY-MM-DD)"),
    end_date: str = Query("2026-06-10", description="Billing range end date (YYYY-MM-DD)"),
    authorization: Optional[str] = Header(None, description="Bearer token authorization")
):
    # Basic Authorization check (simulated)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing API credentials.")

    # High fidelity hardcoded response representing granular billing capabilities
    return BillingResponse(
        client_id="client_enterprise_acme",
        billing_period=BillingPeriod(
            start=f"{start_date}T00:00:00Z",
            end=f"{end_date}T23:59:59Z"
        ),
        usage_summary=UsageSummary(
            total_translation_characters=12543000,
            total_writing_improved_characters=3400000,
            total_api_calls=84500
        ),
        cost_breakdown_usd=CostBreakdown(
            translation_cost=250.86,
            writing_cost=68.00,
            base_subscription=150.00,
            total_due=468.86
        ),
        currency="USD"
    )


# =====================================================================
# 5. Audit Logs Endpoint
# =====================================================================

class AuditFilter(BaseModel):
    residency: Optional[str] = "eu"
    event_type: Optional[str] = "translation_processing"

class AuditRequest(BaseModel):
    client_id: str = Field(..., description="Enterprise Client Identifier.")
    compliance_framework: str = Field("GDPR", description="Target compliance standard (e.g., 'GDPR', 'HIPAA').")
    limit: int = Field(10, ge=1, le=100, description="Max logs returned.")
    filter: Optional[AuditFilter] = None

class AuditLogEntry(BaseModel):
    timestamp: str
    event_id: str
    action: str
    server_location: str
    data_deleted_at: str
    gdpr_compliant: bool

class AuditResponse(BaseModel):
    audit_id: str
    compliance_framework: str
    verified_residency: str
    logs: List[AuditLogEntry]

@app.post("/api/v1/audit/logs", response_model=AuditResponse, tags=["Audit & Compliance"])
async def query_audit_logs(request: AuditRequest):
    # Simulated audit response showing EU data residency compliance (GDPR)
    return AuditResponse(
        audit_id="audit_log_2026_06_10",
        compliance_framework=request.compliance_framework,
        verified_residency=(request.filter.residency if request.filter else "eu"),
        logs=[
            AuditLogEntry(
                timestamp="2026-06-10T12:30:15Z",
                event_id="evt_908123",
                action="translate_request",
                server_location="Frankfurt, Germany (AWS eu-central-1)",
                data_deleted_at="2026-06-10T12:30:16Z",
                gdpr_compliant=True
            ),
            AuditLogEntry(
                timestamp="2026-06-10T12:31:00Z",
                event_id="evt_908124",
                action="translate_request",
                server_location="Frankfurt, Germany (AWS eu-central-1)",
                data_deleted_at="2026-06-10T12:31:01Z",
                gdpr_compliant=True
            )
        ]
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
