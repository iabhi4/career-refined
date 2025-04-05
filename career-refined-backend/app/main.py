from fastapi import FastAPI
from app.api.v1.user import user
from app.api.v1.auth import auth
from app.api.v1.application import application
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.include_router(user)
app.include_router(auth)
app.include_router(application)

@app.get("/")
async def root():
    return {"message": "Career Refined Backend is running!"}