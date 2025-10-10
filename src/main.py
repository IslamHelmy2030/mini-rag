from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory


app = FastAPI()


async def startup_event():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings)
    #generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    #embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)



async def shutdown_event():
    app.mongo_conn.close()

app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)
app.include_router(base.base_router)
app.include_router(data.data_router)












if __name__ == "__main__":
    import uvicorn

    # Note: For auto-reload or multiple workers, run via CLI with an import string, e.g.:
    #   uvicorn main:app --app-dir src --reload
    # Programmatic run below intentionally avoids reload to prevent import-string requirement errors.
    uvicorn.run(app, host="127.0.0.1", port=8000)