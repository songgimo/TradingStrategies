import logging
from src.config.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from enum import Enum

logger = logging.getLogger(__name__)


class GeminiModel(Enum):
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"

    def __str__(self):
        return self.value


class LLMClients:
    @staticmethod
    def google_llm_client(model_name: GeminiModel = GeminiModel.GEMINI_2_5_FLASH, temperature = 0.7) -> ChatGoogleGenerativeAI:
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=settings.google_api_key.get_secret_value(),
        )

        logger.info(f"LLM Client initialized with model name: {model_name}")

        return llm
