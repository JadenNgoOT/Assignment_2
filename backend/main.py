from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import time
from datetime import datetime
from .models import AnalyzeRequest, AnalyzeResponse, LogEntry, Summary
from .safety import safety_checker
from .gemini_client import gemini_client
from .telemetry import telemetry_logger

app = FastAPI(title="Legal Document Analyzer", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve the frontend
@app.get("/")
async def root():
    
    return FileResponse("frontend/index.html")

# Main endpoint: Analyze a legal document
@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_document(request: AnalyzeRequest):
    start_time = time.time()
    
    # Safety checks
    valid, error_msg = safety_checker.validate_input(request.text)
    if not valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Analyze with Gemini
    summary, terms_looked_up, usage_metadata = gemini_client.analyze_document(request.text)
    
    # Determine pathway
    pathway = "legal_term_lookup" if terms_looked_up else "none"
    
    # Calculate metrics
    tokens_used = usage_metadata.get('total_tokens', 0)
    latency_ms = (time.time() - start_time) * 1000
    timestamp = datetime.now().isoformat()
    
    # Generate summary ID and save
    summary_id = telemetry_logger.generate_summary_id()
    summary_obj = Summary(
        id=summary_id,
        timestamp=timestamp,
        document_name=request.document_name,
        summary=summary,
        terms_looked_up=terms_looked_up,
        tokens_used=tokens_used,
        input_length=len(request.text)
    )
    telemetry_logger.save_summary(summary_obj)
    
    # Log telemetry
    log_entry = LogEntry(
        timestamp=timestamp,
        pathway=pathway,
        latency_ms=latency_ms,
        tokens_used=tokens_used,
        input_length=len(request.text),
        success=True
    )
    telemetry_logger.log_request(log_entry)
    
    return AnalyzeResponse(
        summary=summary,
        terms_looked_up=terms_looked_up,
        tokens_used=tokens_used,
        saved_id=summary_id,
        timestamp=timestamp
    )

# Get all saved summaries
@app.get("/api/summaries")
async def get_summaries():
    
    summaries = telemetry_logger.get_all_summaries()
    return {"summaries": summaries}