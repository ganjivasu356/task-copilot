from multi_agent_orchestrator.agents import ChainAgent, ChainAgentOptions, AgentCallbacks
from multi_agent_orchestrator.agents import BedrockLLMAgent, BedrockLLMAgentOptions
from api_agent import ApiAgent, ApiAgentOptions
import asyncio
import chainlit as cl
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
if not GNEWS_API_KEY:
  raise ValueError("GNEWS_API_KEY environment variable not set")

class ChainlitAgentCallbacks(AgentCallbacks):
    def on_llm_new_token(self, token: str) -> None:
        asyncio.run(cl.user_session.get("current_msg").stream_token(token))


agent1 = ApiAgent(ApiAgentOptions(
    endpoint = f"https://gnews.io/api/v4/search?q=example&apikey={GNEWS_API_KEY}",
    method = "GET",
    name = "News Reader Agent",
    description = "Specializes in reading news from various sources",
    streaming=False
  ))

agent2 = BedrockLLMAgent(BedrockLLMAgentOptions(
  name="News Summarization Agent",
  streaming=True,
  description="You are a skilled journalist tasked with creating concise, engaging news summaries."\
      "Given the following text, produce a clear and informative summary that captures the key points," \
      "main actors, and significant details. Your summary should be objective, well-structured, "\
      "and easily digestible for a general audience. Aim for clarity and brevity while maintaining the essence of the news story.",
  model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
  callbacks=ChainlitAgentCallbacks()    
))

options = ChainAgentOptions(
    name='News Reader & Summaiization Agent',
    description='You are an AI agent that reads news from various sources and summarizes them.',
    agents=[agent1, agent2],
    default_output='Sorry, encountered an issue.',
    save_chat=True
)

news_reader_agent = ChainAgent(options)
