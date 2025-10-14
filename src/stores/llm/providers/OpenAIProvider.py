from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):

    def __init__(self, embedding_api_key: str= None, embedding_api_url: str = None,
                 generation_api_key: str = None, generation_api_url: str = None,
                 default_input_max_tokens: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):

        self.embedding_api_key = embedding_api_key
        self.embedding_api_url = embedding_api_url
        self.generation_api_key = generation_api_key
        self.generation_api_url = generation_api_url

        self.default_input_max_tokens = default_input_max_tokens
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        if embedding_api_key:
            self.embedding_client = OpenAI(
                api_key=self.embedding_api_key,
                base_url=self.embedding_api_url if self.embedding_api_url and len(self.embedding_api_url) > 0 else None
            )

        if generation_api_key:
            self.generation_client = OpenAI(
                api_key=self.generation_api_key,
                base_url=self.generation_api_url if self.generation_api_url and len(self.generation_api_url) > 0 else None
            )

        self.enums = OpenAIEnums

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_tokens].strip()

    def generate_text(self, prompt: str, chat_history: list = [],
                      max_output_tokens: int = None, temperature: float = None):
        if not self.generation_client:
            self.logger.error("OpenAI Generation client is not initialized")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI is not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_tokens
        temperature = temperature if temperature is not None else self.default_generation_temperature

        chat_history.append(self.construct_prompt(prompt, OpenAIEnums.USER.value))

        response = self.generation_client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None

        return response.choices[0].message.content


    def embed_text(self, text: str, document_type: str = None):
        if not self.embedding_client:
            self.logger.error("OpenAI Embedding client is not initialized")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI is not set")
            return None

        response = self.embedding_client.embeddings.create(model=self.embedding_model_id, input=text)

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None

        return response.data[0].embedding

    def construct_prompt(self, prompt:str, role:str):
        return {
            "role": role,
            "content": prompt
        }