import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response, status
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.repository import AdminRepository
from app.admin.schemes import AdminRegisterScheme, AdminScheme
from app.auth.bearer import RefreshTokenBearer
from app.auth.schemes import TokenScheme
from app.auth.service import create_access_token, hash_password, verify_password
from app.web.config import Config
from app.web.dependencies import get_admin_repo, get_config, get_session
from app.web.exceptions import EmailAlreadyTakenError, InvalidCredentialsError
from app.web.utils import ResponseScheme

router = APIRouter(prefix="/auth")
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_admin(
    data_admin: AdminRegisterScheme,
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[AdminRepository, Depends(get_admin_repo)],
) -> ResponseScheme[AdminScheme]:
    data_admin.password = hash_password(data_admin.password)
    try:
        admin = await repository.add_admin(session, data_admin)
    except IntegrityError as e:
         logger.warning("Account with this email: [%s] is already taken", data_admin.email)
         raise EmailAlreadyTakenError(data_admin.email) from e
    return ResponseScheme(data=admin)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_admin(
    email: Annotated[EmailStr, Body()],
    password: Annotated[str, Body()],
    response: Response,
    config: Annotated[Config, Depends(get_config)],
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[AdminRepository, Depends(get_admin_repo)],
) -> ResponseScheme[TokenScheme]:
    admin = await repository.get_admin_by_email(session, email)

    if admin is None:
        logger.warning("Invalid login or password for email: [%s]", email)
        raise InvalidCredentialsError

    if not verify_password(password, admin.password):
        logger.warning("Invalid login or password for email: [%s]", email)
        raise InvalidCredentialsError
    token = create_access_token(AdminScheme.model_validate(admin).dict(), config)
    refresh_token = create_access_token(
        AdminScheme.model_validate(admin).dict(),
        config,
        refresh=True,
        expiry=timedelta(days=config.REFRESH_JWT_EXP)
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        # max_age=config.JWT_EXP,  # seconds
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        # max_age=config.REFRESH_JWT_EXP * 24 * 60 * 60,  # days -> seconds
        )
    return ResponseScheme(
        data=TokenScheme(
            access_token=token,
            refresh_token=refresh_token,
            payload=AdminScheme.model_validate(admin),

        )
    )


@router.get("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    request: Request,
    response: Response,
    config: Annotated[Config, Depends(get_config)],
    current_user: Annotated[AdminScheme, Depends(RefreshTokenBearer())],
) -> ResponseScheme[TokenScheme]:
    access_token = create_access_token(current_user.dict(), config)
    refresh_token = create_access_token(
        current_user.dict(),
        config,
        expiry=timedelta(days=config.REFRESH_JWT_EXP),
        refresh=True
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        # max_age=config.JWT_EXP  # seconds
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        # max_age=config.REFRESH_JWT_EXP * 24 * 60 * 60  # days -> seconds
    )
    return ResponseScheme(
        data=TokenScheme(
            access_token=access_token,
            refresh_token=refresh_token,
            payload=current_user,
        )
    )
