from pygments.lexer import default
from alembic.command import init
from datetime import datetime

import uuid


from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
)


table_registry = registry()

@mapped_as_dataclass(table_registry)
class Usuario:
    __tablename__ = 'usuarios'

    id: Mapped[UUID] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    senha_hash: Mapped[str] = mapped_column()
    ativo: Mapped[Boolean] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column( 
        init=False, server_default=func.now(), onupdate=func.now()
    )