from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forms_inventario.database import get_db
from forms_inventario.models import Usuario
from forms_inventario.schemas import (
    LoginRequest,
    TokenResponse,
    UsuarioResponse,
)
from forms_inventario.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/login', response_model=TokenResponse)
async def login(
    req: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]
):
    stmt = select(Usuario).where(Usuario.email == req.email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(req.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email ou senha incorretos',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/me', response_model=UsuarioResponse)
async def get_me(current_user: Annotated[Usuario, Depends(get_current_user)]):
    return current_user
