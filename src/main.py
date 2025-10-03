from fastapi import FastAPI
from routes import base, data

app = FastAPI()

app.include_router(base.base_router)
app.include_router(data.data_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)