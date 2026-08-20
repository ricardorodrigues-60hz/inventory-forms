from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forms_inventario.database import get_session
from forms_inventario.models import Usuario
from forms_inventario.schemas import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from forms_inventario.security import get_current_user, get_password_hash

router = APIRouter(
    prefix='/usuarios',
    tags=['usuarios'],
    dependencies=[Depends(get_current_user)],
)

T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


@router.post('/', response_model=UsuarioResponse, status_code=HTTPStatus.CREATED)
async def create_usuario(user_in: UsuarioCreate, session: T_Session):
    db_user = await session.scalar(select(Usuario).where(Usuario.email == user_in.email))

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email ja cadastrado',
        )

    db_user = Usuario(
        nome=user_in.nome,
        email=user_in.email,
        senha_hash=get_password_hash(user_in.senha),
        ativo=user_in.ativo,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.get('/', response_model=list[UsuarioResponse])
async def read_usuarios(session: T_Session, skip: int = 0, limit: int = 100):
    query = await session.scalars(select(Usuario).offset(skip).limit(limit))
    return query.all()


@router.get('/{user_id}', response_model=UsuarioResponse)
async def read_usuario(user_id: UUID, session: T_Session):
    user = await session.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuario nao encontrado')
    return user


@router.put('/{user_id}', response_model=UsuarioResponse)
async def update_usuario(user_id: UUID, user_in: UsuarioUpdate, session: T_Session):
    user = await session.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuario nao encontrado')

    update_data = user_in.model_dump(exclude_unset=True)
    if 'senha' in update_data:
        update_data['senha_hash'] = get_password_hash(update_data.pop('senha'))

    for field, value in update_data.items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return user


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_usuario(user_id: UUID, session: T_Session):
    user = await session.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuario nao encontrado')

    user.ativo = False
    await session.commit()
