from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routers

ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

v1_app = FastAPI()
v1_app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@v1_app.get("/")
def home():
    return "you've reached v1 of the api"


for router_name, router in routers.items():
    v1_app.include_router(router, tags=[router_name])
