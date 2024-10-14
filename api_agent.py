from typing import List, Dict, Optional, AsyncIterable, Any, Callable
from dataclasses import dataclass, field
from multi_agent_orchestrator.agents import Agent, AgentOptions
from multi_agent_orchestrator.types import ConversationMessage, ParticipantRole
import aiohttp
import json

# @dataclass
# class ApiAgentOptions(AgentOptions):
#     endpoint: str
#     method: str
#     headers_callback: Optional[Callable[[], Dict[str, str]]] = None
#     input_payload_encoder: Optional[Callable[[str, List[ConversationMessage], str, str, Optional[Dict[str, str]]], Any]] = None
#     output_payload_decoder: Optional[Callable[[Any], Any]] = None
#     streaming: bool = False

class ApiAgentOptions(AgentOptions):
    def __init__(self, endpoint: str, method: str, 
                 name = "Api Agent",
                 description = "Specializes in Fetching data from an API",
                 headers_callback: Optional[Callable[[], Dict[str, str]]] = None,
                 input_payload_encoder: Optional[Callable[[str, List[ConversationMessage], str, str, Optional[Dict[str, str]]], Any]] = None,
                 output_payload_decoder: Optional[Callable[[Any], Any]] = None,
                 streaming: bool = False):
        super().__init__(name, description)  # Initialize AgentOptions
        self.endpoint = endpoint
        self.method = method
        self.headers_callback = headers_callback
        self.input_payload_encoder = input_payload_encoder
        self.output_payload_decoder = output_payload_decoder
        self.streaming = streaming


class ApiAgent(Agent):
    def __init__(self, options: ApiAgentOptions):
        super().__init__(options)
        self.options = options
        self.options.input_payload_encoder = options.input_payload_encoder or self.default_input_payload_encoder
        self.options.output_payload_decoder = options.output_payload_decoder or self.default_output_payload_decoder

    @staticmethod
    def default_input_payload_encoder(input_text: str, chat_history: List[ConversationMessage],
                                      user_id: str, session_id: str,
                                      additional_params: Optional[Dict[str, str]] = None) -> Dict:
        return {"input": input_text, "history": chat_history}

    @staticmethod
    def default_output_payload_decoder(response: Any) -> Any:
        if isinstance(response, str):
            return response
        return response.get('output')

    async def fetch(self, payload: Any) -> AsyncIterable[Any]:
        headers = self.get_headers()
        async with aiohttp.ClientSession() as session:
            async with session.request(self.options.method, self.options.endpoint,
                                    headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"HTTP error! status: {response.status}")
                content = await response.text()
                return self.options.output_payload_decoder(content)

    def get_headers(self) -> Dict[str, str]:
        default_headers = {'Content-Type': 'application/json'}
        if self.options.headers_callback:
            return {**default_headers, **self.options.headers_callback()}
        return default_headers

    async def process_request(
        self,
        input_text: str,
        user_id: str,
        session_id: str,
        chat_history: List[ConversationMessage],
        additional_params: Optional[Dict[str, str]] = None
    ) -> ConversationMessage | AsyncIterable[Any]:
        payload = self.options.input_payload_encoder(input_text, chat_history, user_id, session_id, additional_params)

        result = await self.fetch(payload)
        return ConversationMessage(
            role=ParticipantRole.ASSISTANT.value,
            content=[{"text": result}]
        )
