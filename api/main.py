from fastapi import FastAPI

from . import v1


app = FastAPI()


@app.get("/")
def home():
    return "welcome to the workout api"

app.include_router(v1.router)
