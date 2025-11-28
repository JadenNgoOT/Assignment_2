# Assignment_2
## Legal Document Analyzer

AI-powered legal document summarization with automatic legal term lookup using Google's Gemini API.

### Features
- Analyze contracts, NDAs, employment agreements, and other legal documents
- Automatic legal term lookup and definitions
- Auto-save all summaries with full history
- Telemetry logging (tokens, cost, latency)
- Safety features (input validation, prompt injection detection)
- Comprehensive test suite (16 test cases)

### Tech Stack
- **Backend**: FastAPI (Python)
- **AI Model**: Google Gemini 2.5 Flash
- **Frontend**: HTML
- **Data**: JSON storage

### Quick Start

#### Prerequisites
- Python 3
- Gemini API key

#### Installation
1. **Clone the repository**
```bash
git clone <https://github.com/JadenNgoOT/Assignment_2>
cd Assignment_2
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate 
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Get Gemini API Key**
- Go to https://aistudio.google.com/app/apikey
- Click "Create API Key"
- Copy your key

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API key:
# GEMINI_API_KEY=Insert_your_API_key_here
```

6. **Run the application**
```bash
python run.py
```

7. **Open browser**
Navigate to http://localhost:8000

### Usage

#### Web Interface

1. Start the server
2. Open http://localhost:8000
3. Upload a document or paste text
4. Click "Analyze Document"
5. View summary, terms, and metadata
6. Check "Recent Summaries" for history


### Running Tests
```bash
cd tests
python run_tests.py
```

The test suite includes:
- 16 test cases
- Input validation tests
- Prompt injection detection
- Tool calling verification
- Pattern matching validation

Expected pass rate: >90%

### Safety Features

#### 1. System Prompt with Rules
- Clear DO/DON'T instructions
- Objective analysis only
- No legal advice
- Automatic term lookup

#### 2. Input Validation
- Maximum length: 500,000 characters
- Minimum length: 50 characters
- Clear error messages

#### 3. Prompt Injection Detection
Blocks patterns like:
- "ignore previous instructions"
- "forget everything"
- "you are now"
- etc.

### Telemetry

Every request logs:
- Timestamp
- Pathway (tool used or none)
- Latency (milliseconds)
- Tokens used
- Success/failure status

View logs in `data/logs.json`

### Enhancement: Legal Term Lookup

The system automatically:
1. Scans documents for legal jargon
2. Looks up definitions via dictionary API
4. Includes definitions in summary

### Data Storage

All summaries auto-save to `data/summaries.json`:
```json
{
  "id": "sum_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z",
  "document_name": "nda.txt",
  "summary": "...",
  "terms_looked_up": ["indemnification"],
  "tokens_used": 1250,
  "input_length": 450
}
```