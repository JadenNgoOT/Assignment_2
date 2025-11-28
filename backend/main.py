from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import time
from datetime import datetime
import os

from .models import AnalyzeRequest, AnalyzeResponse
from .safety import safety_checker
from .gemini_client import gemini_client
from .telemetry import telemetry_logger
from .models import LogEntry, Summary

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

@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse("frontend/index.html")

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_document(request: AnalyzeRequest):
    """
    Main endpoint: Analyze a legal document
    """
    start_time = time.time()
    pathway = "none"
    success = True
    error_message = None
    tokens_used = None
    cost_estimate = None
    
    try:
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
        
        # Generate summary ID and save
        summary_id = telemetry_logger.generate_summary_id()
        timestamp = datetime.now().isoformat()
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        success = False
        error_message = str(e)
        latency_ms = (time.time() - start_time) * 1000
        
        # Log error
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            pathway="error",
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            input_length=len(request.text),
            success=False,
            error_message=error_message
        )
        telemetry_logger.log_request(log_entry)
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {error_message}")

@app.get("/api/summaries")
async def get_summaries():
    """Get all saved summaries"""
    summaries = telemetry_logger.get_all_summaries()
    return {"summaries": summaries}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}