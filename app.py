from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class user(BaseModel):
    name: str
    age: int
@app.get("/")
def read_root():
    return {"message": "Hello from Kubernetes 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}
