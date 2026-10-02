from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.base import Base
from app.db.database import engine
from app.routes.auth import router as auth_router
from app.routes.diagnostics import router as diagnostics_router
from app.routes.bookings import router as booking_router
from app.routes.payments import router as payment_router
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(diagnostics_router)
app.include_router(booking_router)
app.include_router(payment_router)

@app.get("/")
def root():
    return {
        "message": "EVE Healthcare API is running"
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }