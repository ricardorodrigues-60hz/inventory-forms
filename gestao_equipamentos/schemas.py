from typing import Optional, Literal
from pydantic import BaseModel

class EquipamentoCreate(BaseModel):
    cd_patrimonio: str
    cd_setor: str
    local_especifico: Optional[str] = None
    tipo_maquina: Literal["SLIM", "MASTER"]
    observacao: Optional[str] = None
    cd_serie: Optional[str] = None
    cd_mac: Optional[str] = None
    nr_ip: Optional[str] = None
    nm_hostname: Optional[str] = None
    dt_entrega: Optional[str] = None
    sn_inserido_manual: Optional[Literal["S", "N"]] = "N"

class EquipamentoUpdate(BaseModel):
    cd_patrimonio: Optional[str] = None
    cd_setor: Optional[str] = None
    local_especifico: Optional[str] = None
    tipo_maquina: Optional[Literal["SLIM", "MASTER"]] = None
    observacao: Optional[str] = None
    cd_serie: Optional[str] = None
    cd_mac: Optional[str] = None
    nr_ip: Optional[str] = None
    nm_hostname: Optional[str] = None
    dt_entrega: Optional[str] = None
    sn_inserido_manual: Optional[Literal["S", "N"]] = None

# --- ROLLOUT SCHEMAS ---

class NovoEquipamentoImport(BaseModel):
    cd_patrimonio: str
    cd_serie: Optional[str] = None
    cd_mac: Optional[str] = None
    ano_rollout: Optional[int] = 2026

class ImportarNovosRequest(BaseModel):
    itens: list[NovoEquipamentoImport]

class ImportarNovosResponse(BaseModel):
    processados: int
    mensagem: str

class NovoEquipamentoOut(BaseModel):
    cd_registro: int
    cd_patrimonio: str
    cd_serie: Optional[str] = None
    cd_mac: Optional[str] = None
    ano_rollout: Optional[int] = None
    st_utilizado: str
    reg_key: Optional[int] = None

class ParMerge(BaseModel):
    reg_key_antigo: int
    cd_registro_novo: int

class RolloutMergeRequest(BaseModel):
    pares: list[ParMerge]

class RolloutMergeResponse(BaseModel):
    vinculados: int
    mensagem: str

class ItemPlanejadoOut(BaseModel):
    cd_registro_antigo: int
    cd_patrimonio_antigo: str
    cd_setor: str
    local_especifico: Optional[str] = None
    tipo_maquina: Optional[str] = None
    ano_rollout_antigo: Optional[int] = None
    cd_registro_novo: int
    cd_patrimonio_novo: str
    cd_serie_novo: Optional[str] = None
    cd_mac_novo: Optional[str] = None
    st_utilizado_novo: str

class ConfirmarDevolucaoRequest(BaseModel):
    cd_registro_antigo: int

class ConfirmarDevolucaoResponse(BaseModel):
    sucesso: bool
    mensagem: str

class ConfirmarEntregaRequest(BaseModel):
    cd_registro_novo: int

class ConfirmarEntregaResponse(BaseModel):
    sucesso: bool
    mensagem: str

