import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func

from forms_inventario.database import table_registry
from forms_inventario.models.usuario import Usuario


class TipoMaquina(str, Enum):
    MASTER = 'MASTER'
    SLIM = 'SLIM'


@mapped_as_dataclass(table_registry)
class Registro:
    __tablename__ = 'registros'

    num_patrimonio: Mapped[str] = mapped_column(unique=True, index=True)
    setor: Mapped[str]
    local_especifico: Mapped[str]
    tipo_maquina: Mapped[TipoMaquina]
    registrado_por_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('usuarios.id'))
    registrado_em_dispositivo: Mapped[datetime]
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default_factory=uuid.uuid4, init=False)
    observacao: Mapped[str | None] = mapped_column(default=None)
    sincronizado_em: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), index=True
    )
    atualizado_em: Mapped[datetime | None] = mapped_column(
        init=False, default=None, onupdate=func.now()
    )
    registrado_por: Mapped['Usuario'] = relationship(init=False, lazy='selectin')
