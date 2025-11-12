from fastapi import FastAPI
from app.routers import evaluation, leaderboard
from fastapi.middleware.cors import CORSMiddleware # Will be configured later

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
app.include_router(evaluation.router, prefix="/api/v1")
app.include_router(leaderboard.router, prefix="/api/v1")

@app.get("/api/v1/health")
def get_health():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}