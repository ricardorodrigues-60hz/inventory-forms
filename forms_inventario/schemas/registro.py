from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from forms_inventario.models import TipoMaquina


class RegistroBase(BaseModel):
    num_patrimonio: str
    setor: str
    local_especifico: str
    tipo_maquina: TipoMaquina
    observacao: str | None = None
    registrado_em_dispositivo: datetime


class RegistroCreate(RegistroBase):
    pass


class RegistroUpdate(BaseModel):
    num_patrimonio: str | None = None
    setor: str | None = None
    local_especifico: str | None = None
    tipo_maquina: TipoMaquina | None = None
    observacao: str | None = None


class RegistroResponse(RegistroBase):
    id: UUID
    registrado_por_id: UUID
    sincronizado_em: datetime
    atualizado_em: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
