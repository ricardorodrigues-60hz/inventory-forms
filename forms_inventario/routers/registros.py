from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forms_inventario.database import get_session
from forms_inventario.models import Registro, Usuario
from forms_inventario.schemas import (
    RegistroCreate,
    RegistroResponse,
    RegistroUpdate,
)
from forms_inventario.security import get_current_user

router = APIRouter(
    prefix='/registros',
    tags=['registros'],
    dependencies=[Depends(get_current_user)],
)

T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


@router.post('/', response_model=RegistroResponse, status_code=HTTPStatus.CREATED)
async def create_registro(
    registro_in: RegistroCreate,
    session: T_Session,
    current_user: CurrentUser,
):
    existing = await session.scalar(
        select(Registro).where(Registro.num_patrimonio == registro_in.num_patrimonio)
    )
    if existing:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Numero de patrimonio ja registrado',
        )

    db_registro = Registro(**registro_in.model_dump(), registrado_por_id=current_user.id)
    session.add(db_registro)
    await session.commit()
    await session.refresh(db_registro)
    return db_registro


@router.post('/batch', response_model=list[RegistroResponse], status_code=HTTPStatus.CREATED)
async def create_registros_batch(
    registros_in: list[RegistroCreate],
    session: T_Session,
    current_user: CurrentUser,
):
    created_registros = []

    for reg_in in registros_in:
        existing = await session.scalar(
            select(Registro).where(Registro.num_patrimonio == reg_in.num_patrimonio)
        )
        if not existing:
            db_reg = Registro(**reg_in.model_dump(), registrado_por_id=current_user.id)
            session.add(db_reg)
            created_registros.append(db_reg)

    await session.commit()

    for reg in created_registros:
        await session.refresh(reg)

    return created_registros


@router.get('/', response_model=list[RegistroResponse])
async def read_registros(session: T_Session, skip: int = 0, limit: int = 100):
    query = await session.scalars(select(Registro).offset(skip).limit(limit))
    return query.all()


@router.get('/{registro_id}', response_model=RegistroResponse)
async def read_registro(registro_id: UUID, session: T_Session):
    registro = await session.get(Registro, registro_id)
    if not registro:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Registro nao encontrado')
    return registro


@router.put('/{registro_id}', response_model=RegistroResponse)
async def update_registro(
    registro_id: UUID,
    registro_in: RegistroUpdate,
    session: T_Session,
):
    registro = await session.get(Registro, registro_id)
    if not registro:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Registro nao encontrado')

    for field, value in registro_in.model_dump(exclude_unset=True).items():
        setattr(registro, field, value)

    await session.commit()
    await session.refresh(registro)
    return registro


@router.delete('/{registro_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_registro(registro_id: UUID, session: T_Session):
    registro = await session.get(Registro, registro_id)
    if not registro:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Registro nao encontrado')

    await session.delete(registro)
    await session.commit()
