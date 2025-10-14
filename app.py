import os
import re
import json
import uuid
import logging
import requests
from dotenv import load_dotenv
from prompt_templates import get_fsd_prompt

# === Load environment variables ===
load_dotenv()
print("Region:", os.getenv("AWS_REGION"))

# === Session Management ===
SESSION_FILE = "session.json"

def get_session_id():
    """Retrieve or create a unique session ID."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            session_data = json.load(file)
            return session_data.get("session_id")
    else:
        new_session_id = str(uuid.uuid4())
        with open(SESSION_FILE, "w") as file:
            json.dump({"session_id": new_session_id}, file)
        return new_session_id


def clear_session():
    """Delete stored session (reset memory)."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    logging.info("🔄 Memory cleared. Starting a new session...")

# === API Gateway URLs ===
AGENT_API_URL = "https://pgj3gxzlv8.execute-api.us-west-2.amazonaws.com/dev"
LANGUAGE_API_URL = "https://0oofy8xdqi.execute-api.us-west-2.amazonaws.com/staging"

# === Language Detection ===
def invoke_language_api(user_query: str) -> str:
    """Detect language via API Gateway."""
    payload = {
        "prompt": f"""
        You are an AI assistant tasked with detecting the language of the following user message.
        Available languages are ['english', 'indonesia', 'other'].
        Default to 'english' if undetected.
        Respond with only the name of the detected language.
        Question: {user_query}
        """
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

# === Main Processing ===
def process_streamlit(user_query: str, session_id: str = None, file_path: str = None):
    """Main handler called by FastAPI or Streamlit."""
    if not session_id:
        session_id = get_session_id()
    if not user_query:
        logging.error("No message received.")
        return "Message is required"

    memory_id = session_id
    logging.info(f"🟢 Incoming user query: {user_query}")

    # === Read file text (FSD context) ===
    file_text = ""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_text = f.read()
        except Exception as e:
            logging.warning(f"⚠️ Unable to read file: {file_path} ({e})")
    else:
        logging.warning(f"⚠️ File path not found: {file_path}")

    # === 1. Detect language ===
    language = invoke_language_api(user_query)

    # === 2. Prepare structured prompt ===
    structured_prompt = get_fsd_prompt(user_query, file_text, language)

    agent_payload = {
        "session_id": session_id,
        "prompt": structured_prompt,
        "memory_id": memory_id,
    }

    # === 3. Invoke Agent API ===
    try:
        response = requests.post(AGENT_API_URL, json=agent_payload, timeout=120)
        result = response.json()
        logging.info(f"🤖 Agent API Response: {result}")
        return result.get("response", "Sorry, I don't understand that topic.")
    except Exception as e:
        logging.error(f"❌ Agent invocation error: {e}")
        return f"Error calling agent API: {e}"
