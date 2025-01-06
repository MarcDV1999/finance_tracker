from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, desc, extract
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, sessionmaker

from src.config import DATABASE_URL
from src.db.models import Base, Expense, User
from src.utils.logger import logger_all


class DatabaseManager:
    """Database manager to handle user and expense operations."""

    def __init__(self):
        """Initialize the database manager and create tables if needed."""
        self.engine = create_engine(f"sqlite:///{DATABASE_URL}")
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        logger_all.info("Database initialized.")

    def add_user(self, username: str, name: str, password: str):
        """Add a new user to the database."""
        session = self.Session()
        try:
            user = User(username=username, name=name, password=password)
            session.add(user)
            session.commit()
            logger_all.info(f"User '{username}' added successfully.")
        except Exception as e:
            session.rollback()
            logger_all.error(f"Error adding user: {e}")
        finally:
            session.close()

    def get_user(self, username: str) -> User | None:
        """Retrieve a user by username."""
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user
            else:
                logger_all.info(f"User '{username}' not found.")
                return None
        finally:
            session.close()

    def add_expense(
        self,
        username: str,
        date: datetime,
        concept: str,
        amount: float,
        category: str,
        description: str | None = None,
    ):
        """Add an expense for a specific user."""
        session = self.Session()
        try:
            user = self.get_user(username)
            if not user:
                logger_all.info(
                    f"Cannot add expense. User '{username}' does not exist."
                )
                return
            expense = Expense(
                user_id=user.id,
                date=date,
                concept=concept,
                amount=amount,
                category=category,
                description=description,
            )
            session.add(expense)
            session.commit()
            logger_all.info(f"Expense added for user '{username}'.")
        except Exception as e:
            session.rollback()
            logger_all.error(f"Error adding expense: {e}")
        finally:
            session.close()

    def add_expenses(self, df: pd.DataFrame, user_id: int, db: Session):
        """
        Save a list of expenses from a DataFrame to the database for a given user.

        Args:
            df (pd.DataFrame): DataFrame containing expenses. It should have the
            columns 'amount', 'category', and 'description'.
            user_id (int): The ID of the user for whom the expenses are being saved.
            db (Session): SQLAlchemy session to interact with the database.

        Returns:
            bool: True if expenses were successfully saved, False otherwise.
        """
        raise NotImplementedError()

    def get_user_expenses(self, username: str, date: datetime) -> pd.DataFrame:
        """
        Retrieve all expenses for a specific user.

        The expenses are for the same month and year as the given date,
        and return them as a DataFrame.
        """
        session = self.Session()
        columns = [column.name for column in Expense.__table__.columns]

        with session:
            # Get user
            user = self.get_user(username)

            # User don't exist
            if not user:
                return pd.DataFrame(columns=columns)

            # User exist
            # Filter expenses by user and date
            expenses = (
                session.query(Expense)
                .filter(
                    Expense.user_id == user.id,
                    extract("year", Expense.date)
                    == date.year,  # Año de la fecha proporcionada
                    extract("month", Expense.date)
                    == date.month,  # Mes de la fecha proporcionada
                )
                .all()
            )

            # There are no expenses
            if not expenses:
                return pd.DataFrame(columns=columns)

            # Convertir los resultados en un DataFrame
            expenses_data = [
                {
                    column.key: getattr(expense, column.key)
                    for column in inspect(Expense).columns
                }
                for expense in expenses
            ]

            # Crear un DataFrame a partir de los datos obtenidos
            return pd.DataFrame(expenses_data)

    def get_prev_user_expenses(self, username: str, date: datetime) -> pd.DataFrame:
        """Retrieve all expenses for the specific user for the previous month with data
        before the provided date and return them as a DataFrame."""
        session = self.Session()
        columns = [column.name for column in Expense.__table__.columns]

        with session:
            # Get user
            user = self.get_user(username)

            # User don't exist
            if not user:
                return pd.DataFrame(columns=columns), None

            # User exist
            # Filter expenses by user and date
            expenses = (
                session.query(Expense)
                .filter(Expense.user_id == user.id, Expense.date < date)
                .order_by(desc(Expense.date))
                .all()
            )

            # There are no expenses
            if expenses == []:
                return pd.DataFrame(columns=columns), None

            # Get previous date
            prev_date = expenses[0].date

            # Now get only the expenses of the user of the
            # prev_date
            # Filter expenses by user and date
            prev_expenses = (
                session.query(Expense)
                .filter(
                    Expense.user_id == user.id,
                    extract("year", Expense.date) == prev_date.year,
                    extract("month", Expense.date) == prev_date.month,
                )
                .order_by(desc(Expense.date))
                .all()
            )

            # Convertir los resultados en un DataFrame
            expenses_data = [
                {
                    column.key: getattr(expense, column.key)
                    for column in inspect(Expense).columns
                }
                for expense in prev_expenses
            ]

            # Crear un DataFrame a partir de los datos obtenidos
            return pd.DataFrame(expenses_data), date

    def delete_user(self, username: str):
        """Delete a user and all their expenses."""
        session = self.Session()
        try:
            user = self.get_user(username)
            if not user:
                logger_all.warning(f"Cannot delete. User '{username}' not found.")
                return
            session.query(Expense).filter_by(user_id=user.id).delete()
            session.delete(user)
            session.commit()
            logger_all.info(f"User '{username}' and their expenses deleted.")
        except Exception as e:
            session.rollback()
            logger_all.error(f"Error deleting user: {e}")
        finally:
            session.close()

    def delete_expense(self, username: str, concept: str):
        """Delete an expense for a specific user based on the concept."""
        session = self.Session()
        try:
            # Buscar al usuario
            user = self.get_user(username)
            if not user:
                logger_all.info(
                    f"Cannot delete expense. User '{username}' does not exist."
                )
                return

            # Buscar el gasto correspondiente al usuario y el concepto
            # (concepto = category o description)
            expense = (
                session.query(Expense)
                .filter_by(user_id=user.id, category=concept)
                .first()
            )

            if not expense:
                logger_all.info(
                    f"Expense with concept '{concept}' not found for user '{username}'."
                )
                return

            # Eliminar el gasto encontrado
            session.delete(expense)
            session.commit()
            logger_all.info(
                f"Expense with concept '{concept}' deleted for user '{username}'."
            )
        except Exception as e:
            session.rollback()
            logger_all.error(f"Error deleting expense: {e}")
        finally:
            session.close()
