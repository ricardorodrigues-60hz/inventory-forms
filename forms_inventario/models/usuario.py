import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column
from sqlalchemy.sql import func

from forms_inventario.database import table_registry


@mapped_as_dataclass(table_registry)
class Usuario:
    __tablename__ = 'usuarios'

    nome: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    senha_hash: Mapped[str] = mapped_column()
    ativo: Mapped[bool] = mapped_column(default=True)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default_factory=uuid.uuid4, init=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
