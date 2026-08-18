from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TipoMaquina(str, Enum):
    MASTER = 'MASTER'
    SLIM = 'SLIM'


class RegistroBase(BaseModel):
    num_patrimonio: str
    setor: str
    local_especifico: str
    tipo_maquina: TipoMaquina
    observacao: Optional[str] = None
    registrado_em_dispositivo: datetime


class RegistroCreate(RegistroBase):
    pass


class RegistroUpdate(BaseModel):
    num_patrimonio: Optional[str] = None
    setor: Optional[str] = None
    local_especifico: Optional[str] = None
    tipo_maquina: Optional[TipoMaquina] = None
    observacao: Optional[str] = None


class RegistroResponse(RegistroBase):
    id: UUID
    registrado_por_id: UUID
    sincronizado_em: datetime
    atualizado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
