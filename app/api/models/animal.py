from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db import Base


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    race = Column(String(100), nullable=False)  # Store enum value as string
    status = Column(Integer, nullable=False)  # Store enum value as int (1 or 0)
    birth_date = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
