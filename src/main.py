from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from routes import base, data, nlp
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

app = FastAPI()


async def startup_events():
    settings = get_settings()
    # app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    # app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.db_client)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # vector DB client
    app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vectordb_client.connect()

    # Template Parser
    app.template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG)


async def shutdown_events():
    # app.mongo_conn.close()
    app.db_engine.dispose()
    await app.vectordb_client.disconnect()


app.add_event_handler("startup", startup_events)
app.add_event_handler("shutdown", shutdown_events)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)

if __name__ == "__main__":
    import uvicorn

    # Note: For auto-reload or multiple workers, run via CLI with an import string, e.g.:
    #   uvicorn main:app --app-dir src --reload
    # Programmatic run below intentionally avoids reload to prevent import-string requirement errors.
    uvicorn.run(app, host="127.0.0.1", port=8000)
