# app/main.py

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router

app = FastAPI(
    title="Book Narrator Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("output/audio").mkdir(parents=True, exist_ok=True)
app.mount(
    "/backend-audio",
    StaticFiles(directory="output/audio"),
    name="backend-audio",
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Book Narrator Backend is running",
        "docs": "/docs",
    }