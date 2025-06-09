from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.store.db.sqlalchemy_db import BaseModel


class AuthorModel(BaseModel):
    __tablename__ = "authors"
    author_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)  # unique=True


class BookModel(BaseModel):
    __tablename__ = "books"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.author_id"))
    year: Mapped[int | None] = mapped_column(nullable=True)
    isbn: Mapped[str | None] = mapped_column(nullable=True)  # unique=True
    amount: Mapped[int] = mapped_column(nullable=False, default=1)
    # description: Mapped[str | None] = mapped_column(nullable=True, server_default="No description")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_books_amount_positive"),
    )


class ReaderModel(BaseModel):
    __tablename__ = "readers"

    reader_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)  # unique=True


class LibraryCardModel(BaseModel):
    __tablename__ = "library_cards"

    library_card_id: Mapped[int] = mapped_column(primary_key=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.reader_id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.book_id"))
    borrow_date: Mapped[datetime] = mapped_column(server_default=func.now())
    return_data: Mapped[datetime | None] = mapped_column(nullable=True, default=None)
