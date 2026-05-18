import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Empresa, EmpresaPerfil, Endereco, Fornecimento, Perfil, Produto
from app.schemas.fornecimento import FornecimentoCreate, FornecimentoUpdate
from app.services.events import publisher


def _ensure_fornecedor(db: Session, empresa_id: uuid.UUID) -> None:
    stmt = (
        select(Empresa)
        .where(Empresa.id == empresa_id)
        .where(Empresa.status == "ATIVO")
    )
    empresa = db.scalar(stmt)
    if not empresa:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Empresa ativa nao encontrada.")

    perfil_stmt = (
        select(EmpresaPerfil.empresa_id)
        .join(Perfil, Perfil.id == EmpresaPerfil.perfil_id)
        .where(EmpresaPerfil.empresa_id == empresa_id)
        .where(Perfil.nome == "FORNECEDOR")
        .limit(1)
    )
    if db.scalar(perfil_stmt) is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Empresa nao possui perfil FORNECEDOR.")


def _ensure_produto_ativo(db: Session, produto_id: uuid.UUID) -> None:
    produto = db.scalar(select(Produto).where(Produto.id == produto_id).where(Produto.ativo.is_(True)))
    if not produto:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto ativo nao encontrado.")


def _ensure_endereco_da_empresa(db: Session, endereco_id: uuid.UUID, empresa_id: uuid.UUID) -> None:
    endereco = db.scalar(select(Endereco).where(Endereco.id == endereco_id).where(Endereco.empresa_id == empresa_id))
    if not endereco:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Endereco de origem nao pertence a empresa fornecedora.")


def _get_fornecimento(db: Session, fornecimento_id: uuid.UUID) -> Fornecimento:
    fornecimento = db.scalar(
        select(Fornecimento)
        .options(selectinload(Fornecimento.produto), selectinload(Fornecimento.endereco_origem))
        .where(Fornecimento.id == fornecimento_id)
    )
    if not fornecimento:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fornecimento nao encontrado.")
    return fornecimento


def listar_fornecimentos(
    db: Session,
    empresa_id: uuid.UUID | None = None,
    produto_id: uuid.UUID | None = None,
    apenas_ativos: bool = True,
    limit: int = 50,
    offset: int = 0,
) -> list[Fornecimento]:
    stmt = (
        select(Fornecimento)
        .options(selectinload(Fornecimento.produto), selectinload(Fornecimento.endereco_origem))
        .order_by(Fornecimento.data_cadastro.desc())
        .limit(limit)
        .offset(offset)
    )

    if empresa_id:
        stmt = stmt.where(Fornecimento.empresa_fornecedor_id == empresa_id)
    if produto_id:
        stmt = stmt.where(Fornecimento.produto_id == produto_id)
    if apenas_ativos:
        stmt = stmt.where(Fornecimento.ativo.is_(True))

    return list(db.scalars(stmt).all())


def buscar_fornecimento(db: Session, fornecimento_id: uuid.UUID) -> Fornecimento:
    return _get_fornecimento(db, fornecimento_id)


def criar_fornecimento(db: Session, empresa_id: uuid.UUID, dados: FornecimentoCreate) -> Fornecimento:
    _ensure_fornecedor(db, empresa_id)
    _ensure_produto_ativo(db, dados.produto_id)
    _ensure_endereco_da_empresa(db, dados.endereco_origem_id, empresa_id)

    fornecimento = Fornecimento(
        empresa_fornecedor_id=empresa_id,
        produto_id=dados.produto_id,
        endereco_origem_id=dados.endereco_origem_id,
        preco_unitario=dados.preco_unitario,
        quantidade_disponivel=dados.quantidade_disponivel,
        ativo=True,
    )
    db.add(fornecimento)
    db.commit()
    db.refresh(fornecimento)

    publisher.publish(
        "fornecimento_criado",
        {
            "idFornecimento": fornecimento.id,
            "idEmpresaFornecedor": fornecimento.empresa_fornecedor_id,
            "idProduto": fornecimento.produto_id,
            "idEnderecoOrigem": fornecimento.endereco_origem_id,
            "precoUnitario": fornecimento.preco_unitario,
            "quantidadeDisponivel": fornecimento.quantidade_disponivel,
        },
        key=str(fornecimento.id),
    )

    return _get_fornecimento(db, fornecimento.id)


def atualizar_fornecimento(
    db: Session,
    fornecimento_id: uuid.UUID,
    empresa_id: uuid.UUID,
    dados: FornecimentoUpdate,
) -> Fornecimento:
    fornecimento = _get_fornecimento(db, fornecimento_id)
    if fornecimento.empresa_fornecedor_id != empresa_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Este fornecimento pertence a outra empresa.")

    update_data = dados.model_dump(exclude_unset=True)
    if any(valor is None for valor in update_data.values()):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Campos enviados como null nao sao validos.")

    if "produto_id" in update_data:
        _ensure_produto_ativo(db, dados.produto_id)
    if "endereco_origem_id" in update_data:
        _ensure_endereco_da_empresa(db, dados.endereco_origem_id, empresa_id)

    for campo, valor in update_data.items():
        setattr(fornecimento, campo, valor)

    fornecimento.ultima_alteracao = datetime.now(timezone.utc)
    db.commit()
    db.refresh(fornecimento)
    return _get_fornecimento(db, fornecimento.id)


def atualizar_estoque(
    db: Session,
    fornecimento_id: uuid.UUID,
    empresa_id: uuid.UUID,
    quantidade_disponivel: Decimal,
) -> Fornecimento:
    fornecimento = _get_fornecimento(db, fornecimento_id)
    if fornecimento.empresa_fornecedor_id != empresa_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Este fornecimento pertence a outra empresa.")

    quantidade_anterior = fornecimento.quantidade_disponivel
    fornecimento.quantidade_disponivel = quantidade_disponivel
    fornecimento.ultima_alteracao = datetime.now(timezone.utc)

    db.commit()
    db.refresh(fornecimento)

    publisher.publish(
        "estoque_atualizado",
        {
            "idFornecimento": fornecimento.id,
            "idEmpresaFornecedor": fornecimento.empresa_fornecedor_id,
            "idProduto": fornecimento.produto_id,
            "quantidadeAnterior": quantidade_anterior,
            "quantidadeDisponivel": fornecimento.quantidade_disponivel,
        },
        key=str(fornecimento.id),
    )

    return _get_fornecimento(db, fornecimento.id)


def inativar_fornecimento(db: Session, fornecimento_id: uuid.UUID, empresa_id: uuid.UUID) -> None:
    fornecimento = _get_fornecimento(db, fornecimento_id)
    if fornecimento.empresa_fornecedor_id != empresa_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Este fornecimento pertence a outra empresa.")

    fornecimento.ativo = False
    fornecimento.ultima_alteracao = datetime.now(timezone.utc)
    db.commit()
