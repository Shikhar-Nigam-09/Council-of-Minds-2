import json
import logging
from typing import Any, Dict, Optional

from groq import AsyncGroq

from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Thin async wrapper around Groq chat completion API, centralizing model
    configuration, temperature, max_tokens, and structured JSON output.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        model: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sends an asynchronous chat completion request to Groq enforcing
        JSON object response format, and returns the parsed dictionary.
        """
        if not self.client:
            raise RuntimeError(
                "Groq API key is not configured. Please set GROQ_API_KEY in environment or .env file."
            )

        selected_model = model or model_name or settings.REASONING_MODEL_NAME
        logger.debug(
            f"Calling Groq model '{selected_model}' with max_tokens={max_tokens}, temp={temperature}"
        )

        response = await self.client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Received empty response from Groq API.")

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to decode JSON from Groq response: {content}")
            raise ValueError(f"Invalid JSON returned by Groq model: {exc}") from exc


groq_client = GroqClient()
