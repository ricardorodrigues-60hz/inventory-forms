from http import HTTPStatus

import datetime
from typing import Annotated, Any

from jwt import DecodeError, ExpiredSignatureError, decode, encode
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forms_inventario.settings import Settings
from forms_inventario.database import get_session
from forms_inventario.models import Usuario

settings = Settings()

pwd_context = PasswordHash.recommended()

T_Session: Annotated[AsyncSession, Depends(get_session)]

def create_access_token(
    data: dict[str, Any], expires_delta: datetime.timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPITE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='auth/login', refreshUrl='/auth/refresh'
)

async def get_current_user(
    session: T_Session,
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        subject_email = payload.get('sub')
        
        if not subject_email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception

    except ExpiredSignatureError:
        raise credentials_exception

    result = await session.scalar(
        select(Usuario).where(Usuario.email == subject_email)
    )

    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    if not user.ativo:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Usuario inativo'
        )

    return user
