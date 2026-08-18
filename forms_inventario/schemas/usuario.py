from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    ativo: bool | None = None
    senha: str | None = None


class UsuarioResponse(UsuarioBase):
    id: UUID
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)
