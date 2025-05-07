from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

class HelloResponse(BaseModel):
    message: str
    class Config():
        json_schema_extra = {
            "example": {
                "message": "Hello, Cesar"
            }
        }

@app.get("/hello", response_model=HelloResponse)
async def send_hello(name: str = Query(min_length=2)):
    return HelloResponse(message=f"Hello, {name}")
