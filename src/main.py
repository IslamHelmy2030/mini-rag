from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.mongodb_client = AsyncIOMotorClient(get_settings().MONGODB_URL)
    app.mongodb = app.mongodb_client[get_settings().MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_connection():
    app.mongodb_client.close()

app.include_router(base.base_router)
app.include_router(data.data_router)












if __name__ == "__main__":
    import uvicorn

    # Note: For auto-reload or multiple workers, run via CLI with an import string, e.g.:
    #   uvicorn main:app --app-dir src --reload
    # Programmatic run below intentionally avoids reload to prevent import-string requirement errors.
    uvicorn.run(app, host="127.0.0.1", port=8000)