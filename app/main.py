from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Hello: 
    name: str

    def __init__(self, name: str):
        self.name = name

class HelloRequest(BaseModel):
    name: str = Field(min_length=1)

    class Config():
        json_schema_extra = {
            "example": {
                "name": "Cesar"
            }
        }

@app.get("/hello/{name}")
async def hello(name: str):
    return {"message": f"Hello, {name}"}
