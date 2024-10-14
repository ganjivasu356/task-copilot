
from multi_agent_orchestrator.agents import (BedrockLLMAgent,
 BedrockLLMAgentOptions,
 AgentResponse,
 AgentCallbacks)
import asyncio
import chainlit as cl


class ChainlitAgentCallbacks(AgentCallbacks):
    def on_llm_new_token(self, token: str) -> None:
        asyncio.run(cl.user_session.get("current_msg").stream_token(token))

email_agent = BedrockLLMAgent(BedrockLLMAgentOptions(
  name="Email Agent",
  streaming=True,
  description="Specializes in formatting emails, generating email templates. It can also help in replying to emails.",
  model_id="meta.llama3-1-70b-instruct-v1:0",
  callbacks=ChainlitAgentCallbacks()
))
