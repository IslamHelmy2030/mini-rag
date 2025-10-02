from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv(".env")


from routes import base


app = FastAPI()

app.include_router(base.base_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)