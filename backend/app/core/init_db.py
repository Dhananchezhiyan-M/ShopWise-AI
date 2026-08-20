import logging
from app.core.database import engine, Base
import app.models  # Ensures all models are registered in Base.metadata

logger = logging.getLogger("shopwise.init_db")


def init_db():
    """
    Creates all relational tables and indexes in SQLite/PostgreSQL
    if they do not already exist.
    """
    logger.info("Initializing relational database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully in shopwise.db!")
