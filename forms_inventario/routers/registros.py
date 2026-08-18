from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forms_inventario.database import get_db
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


@router.post(
    '/', response_model=RegistroResponse, status_code=status.HTTP_201_CREATED
)
async def create_registro(
    registro_in: RegistroCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    # Checar se ja existe
    stmt = select(Registro).where(
        Registro.num_patrimonio == registro_in.num_patrimonio
    )
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Numero de patrimonio ja registrado',
        )

    db_registro = Registro(
        **registro_in.model_dump(), registrado_por_id=current_user.id
    )
    db.add(db_registro)
    await db.commit()
    await db.refresh(db_registro)
    return db_registro


@router.post(
    '/batch',
    response_model=list[RegistroResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_registros_batch(
    registros_in: list[RegistroCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    created_registros = []

    # Processa um por um para facilitar fallback de erros
    # Em uma aplicacao real de larga escala, poderiamos usar insert().values()
    # com on_conflict_do_nothing
    for reg_in in registros_in:
        stmt = select(Registro).where(
            Registro.num_patrimonio == reg_in.num_patrimonio
        )
        result = await db.execute(stmt)
        if not result.scalars().first():
            db_reg = Registro(
                **reg_in.model_dump(), registrado_por_id=current_user.id
            )
            db.add(db_reg)
            created_registros.append(db_reg)

    await db.commit()

    for reg in created_registros:
        await db.refresh(reg)

    return created_registros


@router.get('/', response_model=list[RegistroResponse])
async def read_registros(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    stmt = select(Registro).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get('/{registro_id}', response_model=RegistroResponse)
async def read_registro(
    registro_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    registro = await db.get(Registro, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail='Registro nao encontrado')
    return registro


@router.put('/{registro_id}', response_model=RegistroResponse)
async def update_registro(
    registro_id: UUID,
    registro_in: RegistroUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    registro = await db.get(Registro, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail='Registro nao encontrado')

    update_data = registro_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(registro, field, value)

    await db.commit()
    await db.refresh(registro)
    return registro


@router.delete('/{registro_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_registro(
    registro_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    registro = await db.get(Registro, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail='Registro nao encontrado')

    await db.delete(registro)
    await db.commit()
