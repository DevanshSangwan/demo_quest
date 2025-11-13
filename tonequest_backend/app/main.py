from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.routers import evaluation, leaderboard, auth
from fastapi.middleware.cors import CORSMiddleware # Will be configured later
import os

app = FastAPI(
    title="ToneQuest API",
    description="API for evaluating professional writing skills.",
    version="1.0.0"
)

# Configure CORS (placeholder for now, implemented in Section 6)
# origins =
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#    ...
# )

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