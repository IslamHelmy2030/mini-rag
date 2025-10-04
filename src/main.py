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

    uvicorn.run(app, host="127.0.0.1", port=8000)