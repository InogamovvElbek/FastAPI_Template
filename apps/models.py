import os
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

load_dotenv()


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    products: list["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    price: Decimal = Field(max_digits=12, decimal_places=2)
    photo: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)
    category_id: int = Field(foreign_key="categories.id", ondelete="CASCADE")
    category: Optional[Category] = Relationship(back_populates="products")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    age: Optional[int] = Field(default=None)
    username: str = Field(unique=True, nullable=False)
    password: str = Field(nullable=False)  # HASH
    cars: list["Car"] = Relationship(back_populates="user")


class Car(SQLModel, table=True):
    __tablename__ = "cars"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    model: str = Field(nullable=False)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    user: Optional[User] = Relationship(back_populates="cars")


url = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:1@localhost:5432/postgres")
engine = create_engine(url)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
