from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.routers import evaluation, leaderboard, auth
from fastapi.middleware.cors import CORSMiddleware # Will be configured later
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the app directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="ToneQuest API",
    description="API for evaluating professional writing skills.",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default dev server
    "http://localhost:3000",  # Alternative dev port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the application routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(evaluation.router, prefix="/api/v1")
app.include_router(leaderboard.router, prefix="/api/v1")

@app.get("/api/v1/health")
def get_health():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}

@app.get("/auth-test")
def get_auth_test():
    """
    Serve the authentication test page.
    """
    return FileResponse(os.path.join(os.path.dirname(__file__), "auth_test.html"))