import logging

import cohere

from ..LLMEnums import CoHereEnums, DocumentTypeEnums
from ..LLMInterface import LLMInterface


class CoHereProvider(LLMInterface):

    def __init__(self, embedding_api_key: str = None, embedding_api_url: str = None,
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
            self.embedding_client = cohere.Client(api_key=self.embedding_api_key)

        if generation_api_key:
            self.generation_client = cohere.Client(api_key=self.generation_api_key)

        self.enums = CoHereEnums

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
            self.logger.error("CoHere Generation client is not initialized")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere is not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_tokens
        temperature = temperature if temperature is not None else self.default_generation_temperature

        response = self.generation_client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None

        return response.text

    def embed_text(self, text: str, document_type: str = None):
        if not self.embedding_client:
            self.logger.error("CoHere Embedding client is not initialized")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere is not set")
            return None

        input_type = CoHereEnums.DOCUMENT
        if document_type == DocumentTypeEnums.QUERY:
            input_type = CoHereEnums.QUERY

        response = self.embedding_client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=['float']
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None

        return response.embeddings.float[0]

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": prompt
        }
