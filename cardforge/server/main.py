"""
CardForge REST API
Entry point for the web server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import collection, decks, pricing, ai

app = FastAPI(
    title="CardForge API",
    description="Backend API for CardForge MTG Collection Manager",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(collection.router, prefix="/api/collection", tags=["Collection"])
app.include_router(decks.router, prefix="/api/decks", tags=["Decks"])
app.include_router(pricing.router, prefix="/api/pricing", tags=["Pricing"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Agents"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
