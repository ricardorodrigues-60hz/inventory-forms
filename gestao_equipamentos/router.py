import traceback
from datetime import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

from core import Claims, get_claims
from modules.gestao_equipamentos.schemas import (
    EquipamentoCreate, EquipamentoUpdate,
    ImportarNovosRequest, ImportarNovosResponse, NovoEquipamentoOut,
    RolloutMergeRequest, RolloutMergeResponse, ItemPlanejadoOut,
    ConfirmarDevolucaoRequest, ConfirmarDevolucaoResponse,
    ConfirmarEntregaRequest, ConfirmarEntregaResponse
)
from modules.gestao_equipamentos.repository import EquipamentoRepository, RolloutRepository

router = APIRouter(prefix="/api_hcfmb", tags=["Gestão de Equipamentos"])
repo = EquipamentoRepository()
rollout_repo = RolloutRepository()


@router.post("/equipamentos")
async def criar_equipamento(
    payload: Union[EquipamentoCreate, List[EquipamentoCreate]],
    claims: Claims = Depends(get_claims)
):
    usr_id = claims.sub or claims.id or "DESCONHECIDO"

    try:
        if isinstance(payload, list):
            if not payload:
                raise HTTPException(status_code=400, detail="Array de itens vazio.")
            return await repo.criar_lote(payload, str(usr_id))
        else:
            return await repo.criar(payload, str(usr_id))
    except Exception as e:
        print(f"[Equipamentos] Erro ao cadastrar: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar equipamento no banco de dados: {str(e)}")

@router.get("/equipamentos/consultar-patrimonio/{cd_patrimonio}")
async def consultar_patrimonio(
    cd_patrimonio: str,
    claims: Claims = Depends(get_claims)
):
    try:
        res = await repo.consultar_patrimonio(cd_patrimonio)
        if not res:
            raise HTTPException(status_code=404, detail="Patrimônio não encontrado no contrato.")
        return res
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Equipamentos] Erro ao consultar patrimônio: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar patrimônio: {str(e)}")

@router.get("/equipamentos/tecnicos")
async def listar_tecnicos_equipamentos(claims: Claims = Depends(get_claims)):
    try:
        return await repo.listar_tecnicos()
    except Exception as e:
        print(f"[Equipamentos] Erro ao listar técnicos: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar técnicos: {str(e)}")

@router.get("/equipamentos/exportar-excel")
async def exportar_excel_equipamentos(
    q: Optional[str] = None,
    cd_setor: Optional[str] = None,
    registrado_por_id: Optional[str] = None,
    tipo_maquina: Optional[str] = None,
    dt_inicio: Optional[str] = None,
    dt_fim: Optional[str] = None,
    cd_serie: Optional[str] = None,
    nr_ip: Optional[str] = None,
    nm_hostname: Optional[str] = None,
    status_incompleto: Optional[str] = None,
    claims: Claims = Depends(get_claims)
):
    try:
        where_str, params = repo.construir_filtros_equipamentos(
            q=q,
            cd_setor=cd_setor,
            registrado_por_id=registrado_por_id,
            tipo_maquina=tipo_maquina,
            dt_inicio=dt_inicio,
            dt_fim=dt_fim,
            cd_serie=cd_serie,
            nr_ip=nr_ip,
            nm_hostname=nm_hostname,
            status_incompleto=status_incompleto,
        )

        output = await repo.exportar_excel(where_str, params)

        filename = f"Relatorio_Equipamentos_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx"
        headers_resp = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers_resp,
        )
    except Exception as e:
        print(f"[Equipamentos] Erro ao exportar Excel: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao exportar equipamentos para Excel: {str(e)}")

@router.get("/equipamentos")
async def listar_equipamentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=5000),
    q: Optional[str] = None,
    cd_setor: Optional[str] = None,
    registrado_por_id: Optional[str] = None,
    tipo_maquina: Optional[str] = None,
    dt_inicio: Optional[str] = None,
    dt_fim: Optional[str] = None,
    cd_serie: Optional[str] = None,
    nr_ip: Optional[str] = None,
    nm_hostname: Optional[str] = None,
    status_incompleto: Optional[str] = None,
    claims: Claims = Depends(get_claims)
):
    try:
        where_str, params = repo.construir_filtros_equipamentos(
            q=q,
            cd_setor=cd_setor,
            registrado_por_id=registrado_por_id,
            tipo_maquina=tipo_maquina,
            dt_inicio=dt_inicio,
            dt_fim=dt_fim,
            cd_serie=cd_serie,
            nr_ip=nr_ip,
            nm_hostname=nm_hostname,
            status_incompleto=status_incompleto,
        )

        return await repo.listar_equipamentos(skip, limit, where_str, params)
    except Exception as e:
        print(f"[Equipamentos] Erro ao listar: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar equipamentos: {str(e)}")

@router.get("/equipamentos/devolucoes")
@router.get("/devolucoes")
async def obter_devolucoes(claims: Claims = Depends(get_claims)):
    try:
        sheets = await repo.obter_devolucoes()
        return JSONResponse(sheets)
    except Exception as e:
        print(f"[Equipamentos] Erro ao buscar devolucoes: {traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"erro": "Falha ao buscar devoluções", "detalhe": str(e)})

@router.get("/equipamentos/{cd_registro}")
async def obter_equipamento(
    cd_registro: int,
    claims: Claims = Depends(get_claims)
):
    try:
        item = await repo.obter_por_id(cd_registro)
        if not item:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado.")
        return item
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Equipamentos] Erro ao obter: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar equipamento: {str(e)}")

@router.put("/equipamentos/{cd_registro}")
async def atualizar_equipamento(
    cd_registro: int,
    payload: EquipamentoUpdate,
    claims: Claims = Depends(get_claims)
):
    try:
        updated = await repo.atualizar(cd_registro, payload)
        if updated == 0:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado ou nenhuma alteração realizada.")
        return {"mensagem": "Equipamento atualizado com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Equipamentos] Erro ao atualizar: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar equipamento: {str(e)}")

@router.delete("/equipamentos/{cd_registro}")
async def deletar_equipamento(
    cd_registro: int,
    claims: Claims = Depends(get_claims)
):
    try:
        deleted = await repo.deletar(cd_registro)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado.")
        return {"mensagem": "Equipamento excluído com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Equipamentos] Erro ao deletar: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir equipamento: {str(e)}")

@router.get("/setores")
async def listar_setores(claims: Claims = Depends(get_claims)):
    try:
        return await repo.listar_setores()
    except Exception as e:
        print(f"[Setores] Erro ao buscar setores: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar setores: {str(e)}")

@router.post("/equipamentos/sincronizar-legados")
async def sincronizar_equipamentos_legados(claims: Claims = Depends(get_claims)):
    try:
        return await repo.sincronizar_legados()
    except Exception as e:
        print(f"[Equipamentos] Erro na sincronização legados: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar legados: {str(e)}")


# --- ROTAS DE ROLLOUT E SUBSTITUIÇÃO DE EQUIPAMENTOS ---

@router.post("/equipamentos/rollout/importar-novos", response_model=ImportarNovosResponse)
async def importar_novos_equipamentos(
    payload: ImportarNovosRequest,
    claims: Claims = Depends(get_claims)
):
    try:
        affected = await rollout_repo.importar_novos(payload.itens)
        return ImportarNovosResponse(
            processados=affected,
            mensagem=f"Sucesso: {affected} registro(s) inserido(s)/atualizado(s) no estoque novo."
        )
    except Exception as e:
        print(f"[Rollout] Erro ao importar novos equipamentos: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao importar novos equipamentos: {str(e)}")


@router.get("/equipamentos/rollout/disponiveis", response_model=List[NovoEquipamentoOut])
async def listar_equipamentos_novos_disponiveis(
    claims: Claims = Depends(get_claims)
):
    try:
        return await rollout_repo.listar_disponiveis()
    except Exception as e:
        print(f"[Rollout] Erro ao listar disponíveis: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar disponíveis: {str(e)}")


@router.post("/equipamentos/rollout/merge", response_model=RolloutMergeResponse)
async def vincular_pares_rollout(
    payload: RolloutMergeRequest,
    claims: Claims = Depends(get_claims)
):
    try:
        vinculados = await rollout_repo.executar_merge(payload.pares)
        return RolloutMergeResponse(
            vinculados=vinculados,
            mensagem=f"{vinculados} par(es) vinculado(s) com sucesso."
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"[Rollout] Erro ao vincular pares: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao vincular pares: {str(e)}")


@router.get("/equipamentos/rollout/planejados/{cd_setor}", response_model=List[ItemPlanejadoOut])
async def listar_rollout_planejados_por_setor(
    cd_setor: str,
    claims: Claims = Depends(get_claims)
):
    try:
        return await rollout_repo.listar_planejados(cd_setor)
    except Exception as e:
        print(f"[Rollout] Erro ao listar planejados do setor {cd_setor}: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar planejados: {str(e)}")


@router.post("/equipamentos/rollout/confirmar-devolucao", response_model=ConfirmarDevolucaoResponse)
async def confirmar_devolucao_equipamento(
    payload: ConfirmarDevolucaoRequest,
    claims: Claims = Depends(get_claims)
):
    try:
        ok = await rollout_repo.confirmar_devolucao(payload.cd_registro_antigo)
        if not ok:
            raise HTTPException(status_code=404, detail="Equipamento antigo não encontrado.")
        return ConfirmarDevolucaoResponse(
            sucesso=True,
            mensagem="Devolução registrada com sucesso."
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Rollout] Erro ao confirmar devolução: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao confirmar devolução: {str(e)}")


@router.post("/equipamentos/rollout/confirmar-entrega", response_model=ConfirmarEntregaResponse)
async def confirmar_entrega_equipamento(
    payload: ConfirmarEntregaRequest,
    claims: Claims = Depends(get_claims)
):
    try:
        ok = await rollout_repo.confirmar_entrega(payload.cd_registro_novo)
        if not ok:
            raise HTTPException(status_code=404, detail="Equipamento novo não encontrado.")
        return ConfirmarEntregaResponse(
            sucesso=True,
            mensagem="Entrega registrada com sucesso."
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Rollout] Erro ao confirmar entrega: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao confirmar entrega: {str(e)}")

