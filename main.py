from typing import Union

from fastapi import FastAPI


app = FastAPI()

@app.get("/welcome")
def welcome():
    return {
        "message": "Welcome to the mini RAG application!"
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)