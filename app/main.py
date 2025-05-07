from fastapi import FastAPI, Path
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

@app.get("/hello/{name}", response_model=HelloResponse)
async def send_hello(name: str = Path(min_length=2)):
    return HelloResponse(message=f"Hello, {name}")
