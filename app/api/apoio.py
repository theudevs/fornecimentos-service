import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.apoio import EnderecoOpcao, ProdutoOpcao
from app.services.apoio_service import listar_enderecos_empresa, listar_produtos_ativos

router = APIRouter(prefix="/apoio", tags=["Apoio"])


@router.get("/produtos", response_model=list[ProdutoOpcao])
def get_produtos_ativos(db: Session = Depends(get_db)) -> list[ProdutoOpcao]:
    return listar_produtos_ativos(db)


@router.get("/empresas/{empresa_id}/enderecos", response_model=list[EnderecoOpcao])
def get_enderecos_empresa(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[EnderecoOpcao]:
    return listar_enderecos_empresa(db, empresa_id)
