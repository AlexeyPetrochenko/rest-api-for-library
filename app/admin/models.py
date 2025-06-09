from sqlalchemy.orm import Mapped, mapped_column

from app.store.db.sqlalchemy_db import BaseModel


class AdminModel(BaseModel):
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
