from fastapi import FastAPI

from .endpoints import routers

v1_app = FastAPI()


@v1_app.get("/")
def home():
    return "you've reached v1 of the api"


for router_name, router in routers.items():
    v1_app.include_router(router, tags=[router_name])
