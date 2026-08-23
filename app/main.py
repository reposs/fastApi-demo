
from fastapi import FastAPI

from app.api.routers import auth, users

app = FastAPI(title="fastApi-demo")

@app.get("/", tags=["health"])
def root():
    return {"message": "Hello World!, It's a FastAPI demo"}


app.include_router(auth.router)
app.include_router(users.router)

