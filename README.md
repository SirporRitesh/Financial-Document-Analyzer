# Financial-Document-Analyzer

## 🐞 Bugs Found & How I Fixed Them

### 1. **requirements.txt Incompatibility**
- **Problem:** Initial package versions were incompatible with eachother (e.g., CrewAI, CrewAI Tools, FastAPI, LiteLLM, LangChain, google core, ).
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

---
