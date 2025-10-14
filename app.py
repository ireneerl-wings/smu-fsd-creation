import os
import re
import json
import uuid
import logging
import requests
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------------------
load_dotenv()
print("Region:", os.getenv("AWS_REGION", "not set"))

# ------------------------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------------------------------------------------------------
# FastAPI setup
# ------------------------------------------------------------------------------
app = FastAPI(title="FSD Chatbot API", version="1.0")

# Allow CORS for all origins (you can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Folders (relative paths in your repo)
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "Pdf")
TXT_DIR = os.path.join(BASE_DIR, "Txt")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# Mount static folders if needed
if os.path.exists(PDF_DIR):
    app.mount("/pdf", StaticFiles(directory=PDF_DIR), name="pdf")
if os.path.exists(TEMPLATE_DIR):
    templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ------------------------------------------------------------------------------
# Session management
# ------------------------------------------------------------------------------
SESSION_FILE = os.path.join(BASE_DIR, "session.json")


def get_session_id() -> str:
    """Retrieve or create a unique session ID."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            session_data = json.load(file)
            return session_data.get("session_id")
    new_session_id = str(uuid.uuid4())
    with open(SESSION_FILE, "w") as file:
        json.dump({"session_id": new_session_id}, file)
    return new_session_id


def clear_session():
    """Delete stored session (reset memory)."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        logging.info("🔄 Memory cleared. Starting a new session...")

# ------------------------------------------------------------------------------
# External APIs (update with your own endpoints)
# ------------------------------------------------------------------------------
AGENT_API_URL = "https://pgj3gxzlv8.execute-api.us-west-2.amazonaws.com/dev"
LANGUAGE_API_URL = "https://0oofy8xdqi.execute-api.us-west-2.amazonaws.com/staging"

# ------------------------------------------------------------------------------
# Language Detection Helper
# ------------------------------------------------------------------------------
def invoke_language_api(user_query: str) -> str:
    """Detect language via API Gateway."""
    payload = {
        "prompt": (
            "You are an AI assistant tasked with detecting the language "
            "of the following user message. Available languages are "
            "['english', 'indonesia', 'other']. Default to 'english' if "
            "undetected. Respond with only the name of the detected language.\n\n"
            f"Question: {user_query}"
        )
    }
    try:
        response = requests.post(LANGUAGE_API_URL, json=payload, timeout=60)
        result = response.json()
        language = result.get("response", "english").strip().lower()
        if language not in ["english", "indonesia", "other"]:
            language = "english"
        logging.info(f"🌐 Language detected: {language}")
        return language
    except Exception as e:
        logging.error(f"❌ Language detection error: {e}")
        return "english"

# ------------------------------------------------------------------------------
# Main Processing Logic
# ------------------------------------------------------------------------------
def process_fsd_query(user_query: str, session_id: str = None, file_path: str = None):
    """Main FSD chatbot processing logic."""
    if not session_id:
        session_id = get_session_id()
    if not user_query:
        return "Message is required"

    memory_id = session_id
    logging.info(f"🟢 Incoming user query: {user_query}")

    # Read file content if provided
    file_text = ""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_text = f.read()
        except Exception as e:
            logging.warning(f"⚠️ Unable to read file: {file_path} ({e})")

    # Detect language
    language = invoke_language_api(user_query)

    # Build payload for Agent API
    structured_prompt = f"[{language.upper()}]\n\n{user_query}\n\n{file_text}"
    payload = {
        "session_id": session_id,
        "prompt": structured_prompt,
        "memory_id": memory_id,
    }

    try:
        response = requests.post(AGENT_API_URL, json=payload, timeout=290)
        result = response.json()
        logging.info(f"🤖 Agent API Response: {result}")
        return result.get("response", "Sorry, I don't understand that topic.")
    except Exception as e:
        logging.error(f"❌ Agent invocation error: {e}")
        return f"Error calling agent API: {e}"

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    """Render index.html (optional homepage)"""
    if os.path.exists(os.path.join(TEMPLATE_DIR, "index.html")):
        return templates.TemplateResponse("index.html", {"request": None})
    return {"message": "FSD Chatbot API is running 🚀"}

@app.post("/ask_fsd")
async def ask_fsd(user_query: str = Form(...), file: UploadFile = File(None)):
    """
    Main endpoint for frontend form submission.
    Accepts user_query (text) and optional file upload.
    """
    session_id = get_session_id()
    file_path = None

    if file:
        file_path = os.path.join("/tmp", file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

    result = process_fsd_query(user_query, session_id=session_id, file_path=file_path)
    return {"session_id": session_id, "response": result}


@app.get("/health")
def health_check():
    """Health endpoint for AWS App Runner monitoring."""
    return {"status": "ok", "region": os.getenv("AWS_REGION", "unknown")}

# ------------------------------------------------------------------------------
# Local Dev Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))