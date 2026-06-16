from fastapi import FastAPI
from database import engine
import models
from routers import auth, assessment
import os

# Initialize the database tables
models.Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IT Skills Assessment API")

# Read allowed frontend origin from environment, fallback to localhost for dev
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:4000")
if FRONTEND_URL and not FRONTEND_URL.startswith("http"):
    FRONTEND_URL = f"https://{FRONTEND_URL}"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(assessment.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the IT Skills Assessment API"}
