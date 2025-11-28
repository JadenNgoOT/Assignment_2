#!/usr/bin/env python3
"""
One-command startup script for Legal Document Analyzer
"""
import uvicorn
import os
import sys

def check_env():
    """Check if .env file exists and has API key"""
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("   Copy .env.example to .env and add your GEMINI_API_KEY")
        sys.exit(1)
    
    from backend.config import config
    if not config.GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not set in .env file!")
        print("   Get your key at: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    print("Configuration validated\n")

def main():    
    check_env()
    
    print("Starting server...")
    print("Server will be available at: http://localhost:8000")
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()