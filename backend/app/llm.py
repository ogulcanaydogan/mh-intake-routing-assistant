from typing import Dict
from app import config


class MockLLM:
    def generate(self, prompt: str) -> Dict:
        return {
            "intent": "summary",
            "user_message": "Thank you for sharing. Here is a brief neutral summary of what you mentioned.",
            "extracted_entities": {},
            "next_action": {"type": "continue", "payload": {}},
        }


def get_llm_client():
    if config.MOCK_LLM_ENABLED:
        return MockLLM()
    raise NotImplementedError("Only mock LLM is implemented in this MVP")
