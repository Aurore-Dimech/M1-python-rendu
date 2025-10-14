from fastapi import FastAPI, Response

from app.api.init_db import init_db
from app.api.routes import animals
from app.db import Base, engine
from app.utils.logger import get_logger, setup_logging

setup_logging()

logger = get_logger(__name__)

logger.info("Démarrage de l'API")
logger.error("Olala, une erreur")

app = FastAPI(
    title="Ferme",
    description="API REST pour une ferme",
    version="1.0.0",
    docs_url="/docs",
)


def create_tables():
    logger.info("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    init_db()
    logger.info("Database tables created successfully.")


create_tables()


@app.get("/favicon.icon", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    print("QQ a accedé au endpoint")
    return {"message": "Welcome", "version": "1.0.0", "documentation": "/docs"}


# Health Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "bib-api"}


app.include_router(animals.router, prefix="/animals", tags=["Animals"])
