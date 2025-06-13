import logging
import typing

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import AdminModel
from app.admin.schemes import AdminRegisterScheme

if typing.TYPE_CHECKING:
    from app.store.store import Store


logger = logging.getLogger(__name__)


class AdminRepository:
    def __init__(self, store: "Store") -> None:
        self.store = store

    async def add_admin(
        self, session: AsyncSession, admin_data: AdminRegisterScheme
    ) -> AdminModel:
        admin = AdminModel(**admin_data.dict())
        session.add(admin)
        await session.commit()
        return admin

    async def get_admin_by_email(self, session: AsyncSession, email: EmailStr) -> AdminModel | None:
        return await session.scalar(select(AdminModel).where(AdminModel.email == email))
