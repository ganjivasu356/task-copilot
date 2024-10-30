from multi_agent_orchestrator.agents import ChainAgent, ChainAgentOptions, AgentCallbacks
from multi_agent_orchestrator.agents import BedrockLLMAgent, BedrockLLMAgentOptions
from api_agent import ApiAgent, ApiAgentOptions
import asyncio
import chainlit as cl
import os
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Access environment variables
CALENDLY_AUTH_TOKEN = os.getenv('CALENDLY_AUTH_TOKEN')
CALENDLY_USER_URI = os.getenv('CALENDLY_USER_URI')

if not CALENDLY_AUTH_TOKEN:
  raise ValueError("CALENDLY_AUTH_TOKEN environment variable not set")
if not CALENDLY_USER_URI:
  raise ValueError("CALENDLY_USER_URI environment variable not set")

class ChainlitAgentCallbacks(AgentCallbacks):
    def on_llm_new_token(self, token: str) -> None:
        asyncio.run(cl.user_session.get("current_msg").stream_token(token))

def custom_headers_callback():
    return {
        'Authorization': f'Bearer {CALENDLY_AUTH_TOKEN}',
    }

start_time = datetime.now().isoformat()
end_time = (datetime.now() + timedelta(days=10)).isoformat()

agent1 = ApiAgent(ApiAgentOptions(
    endpoint = f"https://api.calendly.com/user_busy_times?user={CALENDLY_USER_URI}&start_time={start_time}&end_time={end_time}",
    method = "GET",
    name = "Calendly Schedule Agent",
    description = "Specializes in Calendar scheduling",
    streaming=False,
    headers_callback=custom_headers_callback,
  ))

agent2 = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="Calendar Summarization",
    streaming=True,
    description="You are an AI agent specialized in summarizing calendar events. Given a list of events, produce a concise summary"\
        " highlighting key details such as event names, dates, times, and participants. Ensure the summary is clear, brief, and "\
            "informative for quick understanding. Do not provide duplicate information or irrelevant details.",
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    callbacks=ChainlitAgentCallbacks()    
))

options = ChainAgentOptions(
    name='Calendar Reader and Summarization Agent',
    description='You are an AI agent that reads calendar events from calendly and summarizes them.',
    agents=[agent1, agent2],
    default_output='Sorry, encountered an issue.',
    save_chat=True
)

calendar_agent = ChainAgent(options)
