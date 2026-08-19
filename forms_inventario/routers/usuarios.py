from http.client import HTTP_PORT
from typing import Annotated
from uuid import UUID

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forms_inventario.database import get_db
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


@router.post(
    '/', response_model=UsuarioResponse, status_code=HTTPStatus.CREATED
)
async def create_usuario(
    user_in: UsuarioCreate, db: Annotated[AsyncSession, Depends(get_db)]
):

    stmt = select(Usuario).where(Usuario.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalars().first():
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
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get('/', response_model=list[UsuarioResponse])
async def read_usuarios(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    stmt = select(Usuario).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get('/{user_id}', response_model=UsuarioResponse)
async def read_usuario(
    user_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    user = await db.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuario nao encontrado')
    return user


@router.put('/{user_id}', response_model=UsuarioResponse)
async def update_usuario(
    user_id: UUID,
    user_in: UsuarioUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await db.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuario nao encontrado')

    update_data = user_in.model_dump(exclude_unset=True)
    if 'senha' in update_data:
        update_data['senha_hash'] = get_password_hash(update_data.pop('senha'))

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_usuario(
    user_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    user = await db.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuario nao encontrado')

    user.ativo = False
    await db.commit()
