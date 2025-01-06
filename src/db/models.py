from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """User table model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)

    # Relationship to link users with their expenses
    expenses = relationship("Expense", back_populates="user")


class Expense(Base):
    """Expense table model."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    concept = Column(String)
    date = Column(Date, nullable=False, default=date.today)  # Default to today's date
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)

    # Back-populates to link to the User table
    user = relationship("User", back_populates="expenses")
