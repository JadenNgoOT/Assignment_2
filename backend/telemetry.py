import json
import os
from datetime import datetime
from typing import Optional
from .config import config
from .models import LogEntry, Summary

# Handles logging of requests and saving summaries
class TelemetryLogger:
    def __init__(self):
        self.log_file = config.LOG_FILE
        self.summaries_file = config.SUMMARIES_FILE
        self._ensure_files_exist()

    # Create data files if they don't exist
    def _ensure_files_exist(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.summaries_file):
            with open(self.summaries_file, 'w') as f:
                json.dump([], f)

    # Append a log entry to logs.json
    def log_request(self, log_entry: LogEntry):
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            logs.append(log_entry.dict())
            
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Error logging request: {e}")

    # Save a document summary to summaries.json
    def save_summary(self, summary: Summary):
        try:
            with open(self.summaries_file, 'r') as f:
                summaries = json.load(f)
            
            summaries.append(summary.dict())
            
            with open(self.summaries_file, 'w') as f:
                json.dump(summaries, f, indent=2)
        except Exception as e:
            print(f"Error saving summary: {e}")

    # Retrieve all saved summaries
    def get_all_summaries(self):
        try:
            with open(self.summaries_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading summaries: {e}")
            return []
        
    # Generate a unique ID for a summary
    def generate_summary_id(self) -> str:
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"sum_{timestamp}"

telemetry_logger = TelemetryLogger()