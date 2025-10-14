import os
import boto3
import logging
from prompt_templates import get_fsd_prompt
import botocore.config
from dotenv import load_dotenv


load_dotenv()
config = botocore.config.Config(read_timeout=600, connect_timeout=120)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

class FSDAgentInvoker:
    def __init__(self):
        self.client = boto3.client(
            "bedrock-agent-runtime",
            region_name=os.getenv("AWS_REGION"),
            config=config
        )
        self.agent_id = os.getenv("FSD_AGENT_ID")
        self.agent_alias_id = os.getenv("FSD_AGENT_ALIAS_ID")


    def format_response(self, user_query, file_text, language, session_id, memory_id):

        structured_prompt = get_fsd_prompt(user_query, file_text, language)

        response = self.client.invoke_agent(
            agentId=self.agent_id,
            agentAliasId=self.agent_alias_id,
            sessionId=session_id, 
            inputText=structured_prompt,
            memoryId  = memory_id,
            enableTrace =True 
        )

        logging.info(f"[ResponseAgentInvoker] format_response RESPONSE: {response}" )

        # full_response = ""
        # for event in response["completion"]:
        #     chunk = event.get("chunk", {}).get("bytes", b"").decode("utf-8").strip()
        #     if chunk:
        #         full_response += chunk

        full_response = ""
        completion_stream = response.get("completion", [])
        if completion_stream:
            for event in completion_stream:
                if 'chunk' in event:
                    chunk_data = event['chunk'].get('bytes', b'').decode('utf-8').strip()
                    if chunk_data:
                        full_response += chunk_data
                        logging.info(f"[ResponseAgentInvoker] Chunk Data: {chunk_data}")
                elif 'trace' in event:
                    trace_info = event['trace']
                    logging.info(f"[ResponseAgentInvoker] Trace Info: {trace_info}")

        # logging.info(f"[ResponseAgentInvoker] format_response before cleaning: {full_response}")

        full_response = full_response.replace("#", "")
        # logging.info(f"\n[ResponseAgentInvoker] format_response: {full_response}")
        return full_response.strip()