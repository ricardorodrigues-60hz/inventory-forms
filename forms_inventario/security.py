import datetime
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forms_inventario.config import settings
from forms_inventario.database import get_db
from forms_inventario.models import Usuario

ALGORITHM = 'HS256'

pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any], expires_delta: datetime.timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Nao foi possivel validar as credenciais',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[ALGORITHM]
        )
        email: str | None = payload.get('sub')
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    stmt = select(Usuario).where(Usuario.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Usuario inativo'
        )

    return user
