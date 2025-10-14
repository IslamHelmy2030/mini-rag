from .LLMEnums import LLMEnums
from .providers import OpenAIProvider, CoHereProvider


class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                embedding_api_key=self.config.EMBEDDING_API_KEY,
                embedding_api_url=self.config.EMBEDDING_API_URL,
                generation_api_key=self.config.GENERATION_API_KEY,
                generation_api_url=self.config.GENERATION_API_URL,
                default_input_max_tokens=self.config.INPUT_DEFAULT_MAX_SIZE,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                embedding_api_key=self.config.EMBEDDING_API_KEY,
                embedding_api_url=self.config.EMBEDDING_API_URL,
                generation_api_key=self.config.GENERATION_API_KEY,
                generation_api_url=self.config.GENERATION_API_URL,
                default_input_max_tokens=self.config.INPUT_DEFAULT_MAX_SIZE,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        return None
