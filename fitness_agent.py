
from multi_agent_orchestrator.agents import (BedrockLLMAgent,
 BedrockLLMAgentOptions,
 AgentResponse,
 AgentCallbacks)
import asyncio
import chainlit as cl


class ChainlitAgentCallbacks(AgentCallbacks):
    def on_llm_new_token(self, token: str) -> None:
        asyncio.run(cl.user_session.get("current_msg").stream_token(token))


fitness_agent = BedrockLLMAgent(BedrockLLMAgentOptions(
  name="Fitness Agent",
  streaming=True,
  description="Specializes in fitness, health, and wellness. It can provide workout routines, diet plans, and general health tips.",
  model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
  callbacks=ChainlitAgentCallbacks()
))
