import re
import json 
import logging 
import uuid 
from datetime import date, datetime, timedelta, timezone
import boto3
import os 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("Region:", os.getenv("AWS_REGION"))

from fsd_agent import FSDAgentInvoker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize agents
fsd_agent = FSDAgentInvoker()

# Initialize Memory Store and Session Management
SESSION_FILE = "session.json"

# Ambil ID sesi, atau buat ID baru kalau belum ada.
def get_session_id():
    if os.path.exists(SESSION_FILE): #jika file session.json ada:
        with open(SESSION_FILE, "r") as file: #buka file 
            session_data = json.load(file) #baca isinya pakae .load
            return session_data.get("session_id") #ambil nilai dari key "session_id" dan return sbgai session ID
    else: #kalau tidak ada
        new_session_id = str(uuid.uuid4()) # Bikin ID baru pakai uuid.uuid4() (ID unik acak).
        with open(SESSION_FILE, "w") as file: #write file 
            json.dump({"session_id": new_session_id}, file)# session_id itu key dari dictionary
        return new_session_id

# menghapus session yang tersimpan (reset session)
def clear_session():
    if os.path.exists(SESSION_FILE): # Kalau file session.json ada → hapus file itu (os.remove).
        os.remove(SESSION_FILE)
    logging.info("🔄 Memory cleared. Starting a new session...")


def invoke_bedrock_language(user_query: str):
    bedrock_client = boto3.client( 
        "bedrock-runtime", 
        region_name=os.getenv("AWS_REGION"), #dari load_dotenv
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    prompt = f"""
        You are an AI assistant tasked with detecting the language of the following user message.
        Avaiable language are ['english', 'indonesia', 'other']. Default 'english' if not detected and 'other'.
        Please respond with just the name of the detected language choosen from 3 avaiable language.
        Question: {user_query}
    """
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200, 
        "top_k": 250, 
        "stop_sequences": [],
        "temperature": 0,
        "top_p": 0.999,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }

    try:
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload),
        )
        result = json.loads(response["body"].read().decode("utf-8")) 
        logging.info(f"Result Bedrock Language Model:")
        logging.info(f"{result}")

        if (
            "content" in result 
            and isinstance(result["content"], list)
            and result["content"]
        ):
            for content_item in result["content"]:
                if content_item.get("type") == "text": 
                    return content_item["text"] 

    except Exception as e:
        return f"An error occurred: {e}"


def process_streamlit(user_query: str, session_id: str = None, file_path: str = None):
    if not session_id:
        session_id = get_session_id()
    if not user_query:
        logging.error("No message received.")
        return "Message is required"
    
    # utc7 = timezone(timedelta(hours=7))
    # timestamp = datetime.now(utc7).strftime("%Y%m%d")
    # session_id = timestamp 
    
    memory_id = session_id
    logging.info(f"🟢 Incoming User Query: {user_query}")

    file_text = ""
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            file_text = f.read()
    else:
        logging.warning(f"⚠️ File path tidak ditemukan: {file_path}")


    #mendeteksi bahasa dari pesan yang dikirim
    language = invoke_bedrock_language(user_query)
    if language not in ["english", "indonesia"]:
        language = "english" 
    logging.info(f"🌐 Language Detected: {language}")
    
    final_result = fsd_agent.format_response(user_query, file_text, language, session_id, memory_id)
    logging.info(f"🤖 Agent Response: {final_result}")

        
    return final_result if final_result else "Sorry, I don't understand that topic."


