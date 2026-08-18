import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from forms_inventario.database import Base


class Registro(Base):
    __tablename__ = 'registros'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    num_patrimonio = Column(String, unique=True, index=True, nullable=False)

    # Setor por enquanto eh VARCHAR simples ate termos a lista de CCs
    setor = Column(String, nullable=False)

    local_especifico = Column(String, nullable=False)
    tipo_maquina = Column(
        Enum('MASTER', 'SLIM', name='tipo_maquina_enum'), nullable=False
    )
    observacao = Column(String, nullable=True)

    registrado_por_id = Column(
        UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False
    )

    # Timestamps (estrategia offline-first)
    registrado_em_dispositivo = Column(DateTime(timezone=True), nullable=False)
    sincronizado_em = Column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento (opcional, util para consultas)
    registrado_por = relationship('Usuario')
