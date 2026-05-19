import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.db.session import get_db
from app.schemas.fornecimento import (
    EstoqueUpdate,
    FornecimentoCreate,
    FornecimentoResponse,
    FornecimentoUpdate,
)
from app.services.fornecimento_service import (
    atualizar_estoque,
    atualizar_fornecimento,
    buscar_fornecimento,
    criar_fornecimento,
    inativar_fornecimento,
    listar_fornecimentos,
)

router = APIRouter(prefix="/fornecimentos", tags=["Fornecimentos"])
empresa_router = APIRouter(prefix="/empresas", tags=["Fornecimentos"])


@router.post("", response_model=FornecimentoResponse, status_code=status.HTTP_201_CREATED)
def post_fornecimento(
    dados: FornecimentoCreate,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> FornecimentoResponse:
    return criar_fornecimento(db, auth.empresa_id, dados)


@router.get("", response_model=list[FornecimentoResponse])
def get_fornecimentos(
    db: Session = Depends(get_db),
    empresa_id: uuid.UUID | None = Query(default=None),
    produto_id: uuid.UUID | None = Query(default=None),
    apenas_ativos: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[FornecimentoResponse]:
    return listar_fornecimentos(db, empresa_id, produto_id, apenas_ativos, limit, offset)


@router.get("/{fornecimento_id}", response_model=FornecimentoResponse)
def get_fornecimento(
    fornecimento_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> FornecimentoResponse:
    return buscar_fornecimento(db, fornecimento_id)


@empresa_router.get("/{empresa_id}/fornecimentos", response_model=list[FornecimentoResponse])
def get_fornecimentos_por_empresa(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
    apenas_ativos: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[FornecimentoResponse]:
    return listar_fornecimentos(db, empresa_id, None, apenas_ativos, limit, offset)


@router.put("/{fornecimento_id}", response_model=FornecimentoResponse)
def put_fornecimento(
    fornecimento_id: uuid.UUID,
    dados: FornecimentoUpdate,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> FornecimentoResponse:
    return atualizar_fornecimento(db, fornecimento_id, auth.empresa_id, dados)


@router.patch("/{fornecimento_id}/estoque", response_model=FornecimentoResponse)
def patch_estoque(
    fornecimento_id: uuid.UUID,
    dados: EstoqueUpdate,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> FornecimentoResponse:
    return atualizar_estoque(db, fornecimento_id, auth.empresa_id, dados.quantidade_disponivel)


@router.delete("/{fornecimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fornecimento(
    fornecimento_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> Response:
    inativar_fornecimento(db, fornecimento_id, auth.empresa_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
