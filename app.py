import uuid
import asyncio
from typing import Optional, List, Dict, Any
import json
import chainlit as cl
import sys
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator, OrchestratorConfig
from multi_agent_orchestrator.agents import AgentResponse
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator
from multi_agent_orchestrator.types import ConversationMessage

from fitness_agent import fitness_agent
from email_agent import email_agent
from news_reader_agent import news_reader_agent
from calendar_agent import calendar_agent

orchestrator = MultiAgentOrchestrator(options=OrchestratorConfig(
  LOG_AGENT_CHAT=True,
  LOG_CLASSIFIER_CHAT=True,
  LOG_CLASSIFIER_RAW_OUTPUT=True,
  LOG_CLASSIFIER_OUTPUT=True,
  LOG_EXECUTION_TIMES=True,
  MAX_RETRIES=3,
  USE_DEFAULT_AGENT_IF_NONE_IDENTIFIED=False,
  NO_SELECTED_AGENT_MESSAGE="Sorry, I am not able to help with that. Please try asking latest news summary, fitness tips or about your schedule.",
  MAX_MESSAGE_PAIRS_PER_AGENT=10
))

orchestrator.add_agent(fitness_agent)
# orchestrator.add_agent(email_agent)
orchestrator.add_agent(news_reader_agent)
orchestrator.add_agent(calendar_agent)

async def handle_request(_orchestrator: MultiAgentOrchestrator, _user_input: str, _user_id: str, _session_id: str):
    # print(f"User Input: {_user_input}")
    response: AgentResponse = await _orchestrator.route_request(_user_input, _user_id, _session_id, {})
    # Print metadata
    print(f"Selected Agent: {response.metadata.agent_name}")
    # print(f"Response: {response}")
    return response


@cl.on_chat_start
async def start():
    cl.user_session.set("user_id", str(uuid.uuid4()))
    cl.user_session.set("session_id", str(uuid.uuid4()))
    cl.user_session.set("chat_history", [])

@cl.on_message
async def main(message: cl.Message):
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("session_id")

    msg = cl.Message(content="")

    await msg.send()  # Send the message immediately to start streaming
    cl.user_session.set("current_msg", msg)

    response: AgentResponse = await handle_request(orchestrator, message.content, user_id, session_id)

    # Handle non-streaming responses
    if isinstance(response, AgentResponse) and response.streaming is False:
        # Handle regular response
        if isinstance(response.output, str):
            await msg.stream_token(response.output)
        elif isinstance(response.output, ConversationMessage):
                await msg.stream_token(response.output.content[0].get('text'))
    await msg.update()


if __name__ == "__main__":
    cl.run()
