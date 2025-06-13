from app.admin.schemes import AdminScheme
from app.base.schemes import BaseScheme


class TokenScheme(BaseScheme):
    access_token: str
    refresh_token: str
    payload: AdminScheme


