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
app = FastAPI(title="FSD Chatbot API", version="1.2")

# Allow Streamlit front-end to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Directory setup
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "Pdf")
TXT_DIR = os.path.join(BASE_DIR, "Txt")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

if os.path.exists(PDF_DIR):
    app.mount("/pdf", StaticFiles(directory=PDF_DIR), name="pdf")

templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ------------------------------------------------------------------------------
# Session management
# ------------------------------------------------------------------------------
SESSION_FILE = os.path.join(BASE_DIR, "session.json")

def get_session_id() -> str:
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)
            return session_data.get("session_id")
    new_session_id = str(uuid.uuid4())
    with open(SESSION_FILE, "w") as f:
        json.dump({"session_id": new_session_id}, f)
    return new_session_id

# ------------------------------------------------------------------------------
# External APIs
# ------------------------------------------------------------------------------
AGENT_API_URL = "https://pgj3gxzlv8.execute-api.us-west-2.amazonaws.com/dev"
LANGUAGE_API_URL = "https://0oofy8xdqi.execute-api.us-west-2.amazonaws.com/staging"

# ------------------------------------------------------------------------------
# Utility functions
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
        response = requests.post(LANGUAGE_API_URL, json=payload, timeout=20)
        result = response.json()
        language = result.get("response", "english").strip().lower()
        if language not in ["english", "indonesia", "other"]:
            language = "english"
        return language
    except Exception as e:
        logging.error(f"❌ Language detection error: {e}")
        return "english"

def chunk_text(text, max_length=4000):
    """Split long text into smaller pieces."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < max_length:
            current += s + " "
        else:
            chunks.append(current.strip())
            current = s + " "
    if current:
        chunks.append(current.strip())
    return chunks

def is_small_talk(query: str) -> bool:
    """Detect if message is small-talk and not FSD-related."""
    small_talk = [
        "hi", "hello", "hey", "good morning", "good evening",
        "thanks", "thank you", "how are you", "yo", "hola"
    ]
    q = query.lower().strip()
    return any(q.startswith(st) or q == st for st in small_talk)

# ------------------------------------------------------------------------------
# Main logic
# ------------------------------------------------------------------------------
def process_fsd_query(user_query: str, session_id=None, file_path=None):
    if not session_id:
        session_id = get_session_id()
    if not user_query:
        return "Message is required"

    # Small talk? respond locally
    if is_small_talk(user_query):
        return "👋 Hi there! I’m your FSD assistant. Select a file on the left and describe your requirement below."

    language = invoke_language_api(user_query)
    logging.info(f"🌐 Language detected: {language}")

    # Read file text
    file_text = ""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_text = f.read()
        except Exception as e:
            logging.warning(f"⚠️ Unable to read file: {e}")

    # Split large text into chunks to prevent timeout
    chunks = chunk_text(file_text)
    responses = []

    for idx, chunk in enumerate(chunks or [""], 1):
        structured_prompt = f"[Part {idx}/{len(chunks)}][{language.upper()}]\n\nUser Query: {user_query}\n\nContext:\n{chunk}"
        payload = {
            "session_id": session_id,
            "prompt": structured_prompt,
            "memory_id": session_id,
        }
        try:
            resp = requests.post(AGENT_API_URL, json=payload, timeout=60)
            result = resp.json()
            responses.append(result.get("response", ""))
        except Exception as e:
            logging.error(f"❌ Agent error (chunk {idx}): {e}")
            responses.append(f"(Chunk {idx} failed to process.)")

    return "\n\n".join(responses).strip()

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    """Render your template if exists."""
    if os.path.exists(os.path.join(TEMPLATE_DIR, "index.html")):
        return templates.TemplateResponse("index.html", {"request": None})
    return {"message": "FSD Chatbot API is running 🚀"}

@app.post("/ask_fsd")
async def ask_fsd(user_query: str = Form(...), file: UploadFile = File(None)):
    session_id = get_session_id()
    file_path = None
    if file:
        file_path = os.path.join("/tmp", file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

    result = process_fsd_query(user_query, session_id, file_path)
    return {"session_id": session_id, "response": result}

@app.get("/health")
def health_check():
    return {"status": "ok", "region": os.getenv("AWS_REGION", "unknown")}

# ------------------------------------------------------------------------------
# Local test entry
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
