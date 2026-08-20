from forms_inventario.database import table_registry
from forms_inventario.models.registro import Registro, TipoMaquina
from forms_inventario.models.usuario import Usuario

__all__ = ['Usuario', 'Registro', 'TipoMaquina', 'table_registry']
