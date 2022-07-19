from fastapi import FastAPI

from . import v1


app = FastAPI()


@app.get("/")
def home():
    return "welcome to the workout api"


app.mount("/v1", v1.app, name="Version 1")
