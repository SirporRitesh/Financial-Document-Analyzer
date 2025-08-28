from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import base64
import json
import logging
from datetime import datetime
from pathlib import Path
import uvicorn
from litellm import completion

MAX_FILE_SIZE = 10 * 1024 * 1024  # This = 10 MB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/financial_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Financial Document Analyzer")

def save_debug_info(debug_data: dict, file_id: str):
    """Save debug information to outputs directory"""
    try:
        os.makedirs("outputs", exist_ok=True)
        debug_file = f"outputs/debug_{file_id}.json"
        with open(debug_file, "w") as f:
            json.dump(debug_data, f, indent=2, default=str)
        logger.info(f"Debug info saved to {debug_file}")
    except Exception as e:
        logger.error(f"Failed to save debug info: {e}")

def extract_text_preview(file_path: str, max_chars: int = 500) -> str:
    """Extract preview of text from PDF for debugging"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            preview = str(content[:max_chars]) + "..." if len(content) > max_chars else str(content)
            return preview[:max_chars]
    except Exception as e:
        logger.error(f"Failed to extract text preview: {e}")
        return "Unable to extract text preview"

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights. Return your answer as plain text only, without any formatting, bullet points, or markdown.")
):
    """Analyze financial document and provide comprehensive investment recommendations"""
    
    file_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    # Initialize debug data
    debug_data = {
        "file_id": file_id,
        "timestamp": start_time.isoformat(),
        "original_filename": file.filename,
        "query": query,
        "file_size": 0,
        "processing_steps": []
    }
    
    logger.info(f"Starting analysis for file: {file.filename} (ID: {file_id})")

    # Validate file type
    if file.content_type != "application/pdf":
        logger.warning(f"Invalid file type: {file.content_type} for file: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Validate file size
    contents = await file.read()
    file_size = len(contents)
    debug_data["file_size"] = file_size
    debug_data["processing_steps"].append(f"File read: {file_size} bytes")
    
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File too large: {file_size} bytes for file: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum allowed size is 10MB."
        )
    
    await file.seek(0)
    file_path = f"data/financial_document_{file_id}.pdf"
    
    logger.info(f"Processing file: {file.filename} ({file_size} bytes) -> {file_path}")

    try:
        os.makedirs("data", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        debug_data["processing_steps"].append("File saved to disk")
        text_preview = extract_text_preview(file_path)
        debug_data["text_preview"] = text_preview
        logger.info(f"Text preview extracted: {len(text_preview)} characters")

        # Read and encode PDF as base64
        pdf_bytes = Path(file_path).read_bytes()
        encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        debug_data["processing_steps"].append("PDF encoded to base64")

        # LiteLLM messages payload
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {
                    "type": "file",
                    "file": {
                        "file_data": f"data:application/pdf;base64,{encoded_pdf}"
                    }
                }
            ]
        }]

        logger.info(f"Calling Gemini API for analysis (file_id: {file_id})")
        debug_data["processing_steps"].append("API call initiated")
        
        # Call Gemini via LiteLLM
        response = completion(
            model="gemini/gemini-2.0-flash",
            provider="google",
            messages=messages,
            api_key=os.getenv("GEMINI_API_KEY")
        )
        response_metadata = {
            "model": "gemini/gemini-2.0-flash",
            "provider": "google",
            "response_type": type(response).__name__
        }
        
        # token usage if available
        try:
            if hasattr(response, 'usage'):
                response_metadata["tokens_used"] = response.usage
            elif hasattr(response, '_hidden_params'):
                response_metadata["hidden_params"] = str(response._hidden_params)[:200]
        except Exception as meta_error:
            logger.warning(f"Could not extract response metadata: {meta_error}")
        
        debug_data["response_metadata"] = response_metadata
        debug_data["processing_steps"].append("API response received")
        
        # calc processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        debug_data["processing_time_seconds"] = processing_time
        debug_data["completion_time"] = end_time.isoformat()
        
        logger.info(f"Analysis completed for {file.filename} in {processing_time:.2f}s (ID: {file_id})")
        
        # debug information save
        save_debug_info(debug_data, file_id)

        return {
            "status": "success",
            "query": query,
            "analysis": response,
            "file_processed": file.filename,
            "file_id": file_id,
            "processing_time": f"{processing_time:.2f}s"
        }

    except Exception as e:
        error_msg = str(e)
        if "api" in error_msg.lower() and "key" in error_msg.lower():
            error_msg = "API authentication error (key-related)"
        
        debug_data["error"] = error_msg
        debug_data["processing_steps"].append(f"Error occurred: {error_msg}")
        
        logger.error(f"Error processing {file.filename} (ID: {file_id}): {error_msg}")
        save_debug_info(debug_data, file_id)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {error_msg}"
        )
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as cleanup_error:
                logger.error(f"Cleanup error for {file_path}: {cleanup_error}")

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    logger.info("Starting Financial Document Analyzer API")
    uvicorn.run(app, host="127.0.0.1", port=8000)
