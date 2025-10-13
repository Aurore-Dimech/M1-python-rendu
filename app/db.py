import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./test.db"
)  # File-based for tests; use :memory: only for dev if needed
if "test" in os.environ.get("PYTEST_CURRENT_TEST", ""):  # Detect test mode
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app.db"  # Dedicated test file
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
