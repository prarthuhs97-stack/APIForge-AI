from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.api_parser import parse_api_code
from security.security_scanner import scan_code
from backend.context_analyzer import analyze_context
from ai.ai_generator import generate_documentation
from quality.quality_checker import calculate_quality
from backend.api_diff import compare_apis
app = FastAPI(title="APIForge AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:8443",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8443",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    code: str
    previous_code: str = ""

@app.get("/")
def home():
    return {"message": "APIForge AI backend is running"}

@app.post("/analyze")
def analyze_api(request: AnalyzeRequest):
    result = parse_api_code(request.code)

    api_changes = {
        "changes": [],
        "breaking_changes": [],
        "has_changes": False
    }

    if request.previous_code.strip():
        previous_result = parse_api_code(request.previous_code)

        api_changes = compare_apis(
            previous_result["endpoints"],
            result["endpoints"]
        )

    security_findings = scan_code(request.code)

    context = analyze_context(
        request.code,
        result["endpoints"]
    )

    result["api_changes"] = api_changes
    result["security"] = security_findings
    result["context"] = context

    result["documentation"] = [
    generate_documentation(
        endpoint,
        context,
        request.code
    )
    for endpoint in result["endpoints"]
]
    result["quality"] = calculate_quality(
    result["endpoints"],
    security_findings,
    context
)
    return result