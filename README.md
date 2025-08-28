# Financial-Document-Analyzer

## Table of Contents

- [Project Overview](#1-project-overview)
- [Bugs Encountered and Fixes](#1-bugs-found--how-i-fixed-them)
- [Setup Instructions](#3-setup-instructions)
- [Usage Instructions](#4-usage-instructions)
- [API Documentation](#5-api-documentation)
- [Folder Structure](#6-folder-structure)

  ---


## 1) Project Overview

### This system allows users to upload financial PDFs and receive structured analysis including:

### Executive Summary

- Financial Analysis (Revenue, Profit, Growth Trends)

- Risk Assessment

- Investment Recommendations

### It integrates AI agents with tools for reading PDFs, analyzing financial statements, and assessing risks.


## 2) Bugs Found & How I Fixed Them

### 1. **requirements.txt Incompatibility**
- **Problem:** Initial package versions were incompatible with eachother (e.g., CrewAI, CrewAI Tools, FastAPI, LiteLLM, LangChain, google core).
- **Fix:** Updated `requirements.txt` to use compatible versions for all dependencies. Verified installation and runtime compatibility.

### 2. **LLM Provider Not Provided**
- **Problem:** LiteLLM requires both a provider (e.g., `"google"`) and a model string (e.g., `"gemini/gemini-2.0-flash"`).  
- **Fix:** Updated all LLM calls to include both provider and correct model string.

### 3. **PDF Path in Prompt**
- **Problem:** Passing a file path to the LLM does not work; LLMs cannot access local files.
- **Fix:** PDF is read, base64-encoded, and sent as inline data to Gemini.

### 4. **CrewAI Tool Invocation**
- **Problem:** CrewAI agents/tools were not being triggered correctly.
- **Fix:** Ensured tools are attached to agents and tasks, and document text is passed in context.

### 5. **ModelResponse Serialization**
- **Problem:** FastAPI cannot serialize LiteLLM's ModelResponse objects.
- **Fix:** Extracted `.text` or `.choices` from the response before returning.

### 6. **Input Validation**
- **Problem:** Non-PDF files and large files were not handled.
- **Fix:** Added validation for file type and size.

### 7. **PDF Extraction Safety**
- **Problem:** Encrypted, malformed, or empty PDFs could crash the app.
- **Fix:** Added robust error handling and safe fallback messages.

### 8. **Logging & Debugging**
- **Problem:** No persistent logs or debug info.
- **Fix:** Added logging and saved debug info to `outputs/`.


# 3) Setup Instructions

- Clone the Repository

```markdown
git clone https://github.com/SirporRitesh/FinancialDocumentAnalyzer.git
cd FinancialDocumentAnalyzer
```


- Create a Virtual Environment and Install Dependencies

```markdown
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```


- Set Environment Variables

- Create a .env file:
```markdown
GEMINI_API_KEY=<your_gemini_api_key>
```


- Run the API
```markdown
uvicorn main:app --reload
```


- Server runs at http://127.0.0.1:8000/.


## 4) Usage Instructions

- Health Check
  
```markdown
GET http://127.0.0.1:8000/
```

```markdown
Response:

{
  "message": "Financial Document Analyzer API is running"
}
```


- Analyze a PDF

```markdown
POST http://127.0.0.1:8000/analyze
Content-Type: multipart/form-data
Form Fields:
  file: <your_pdf_file>
  query: "Analyze this financial document for key metrics and risks"
```


- Response Example:

```markdown

{
  "status": "success",
  "query": "Analyze this financial document for key metrics and risks",
  "analysis": {
    "executive_summary": "...",
    "financial_analysis": "...",
    "risk_assessment": "...",
    "investment_recommendations": "..."
  },
  "file_processed": "sample_compressed.pdf"
}
```


### Notes:

- Only PDFs up to 10MB are allowed.

- Extracted text is cleaned of hallucinated URLs or fabricated content.

- JSON output is saved in outputs/ folder for debugging and future reference.

## 5) API Documentation
### Endpoint	Method	Description	Request	Response

- /	GET	Health check	None	{ "message": "API is running" }
- /analyze	POST	Analyze PDF document	file: UploadFile, query: str	Structured analysis JSON

### Structured Analysis Fields:

- executive_summary: Overall assessment or summary.

- financial_analysis: Revenue, profit, and financial metrics.

- risk_assessment: Identified risks and mitigation strategies.

- investment_recommendations: Evidence-based recommendations.

## 6) Folder Structure
```markdown
FinancialDocumentAnalyzer/
├─ data/                 # Temporary storage for uploaded PDFs
├─ outputs/              # Structured JSON results and debug info
├─ tools/                # PDF reading and analysis tools
├─ agents.py             # CrewAI agent definitions
├─ task.py               # Task definitions for CrewAI
├─ main.py               # FastAPI backend
├─ requirements.txt
├─ README.md

```
