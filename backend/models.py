from pydantic import BaseModel, Field
from typing import Optional, List

# Validates incoming data from the frontend/API
class AnalyzeRequest(BaseModel):
    text: str = Field(..., max_length=50000)
    document_name: Optional[str] = "unnamed_document"

# Defines what the API sends back to the user
class AnalyzeResponse(BaseModel):
    summary: str
    terms_looked_up: List[str] = []
    tokens_used: Optional[int] = None
    saved_id: str
    timestamp: str

# Structure for data saved to summaries.json
class Summary(BaseModel):
    id: str
    timestamp: str
    document_name: str
    summary: str
    terms_looked_up: List[str]
    tokens_used: Optional[int]
    input_length: int

# Structure for telemetry data saved to logs.json
class LogEntry(BaseModel):
    timestamp: str
    pathway: str  # "legal_term_lookup", "none", "error"
    latency_ms: float
    tokens_used: Optional[int]
    input_length: int
    success: bool
    error_message: Optional[str] = None