import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Endereco, Produto


def listar_produtos_ativos(db: Session) -> list[Produto]:
    stmt = (
        select(Produto)
        .where(Produto.ativo.is_(True))
        .order_by(Produto.nome)
    )
    return list(db.scalars(stmt).all())


def listar_enderecos_empresa(db: Session, empresa_id: uuid.UUID) -> list[Endereco]:
    stmt = (
        select(Endereco)
        .where(Endereco.empresa_id == empresa_id)
        .order_by(Endereco.estado, Endereco.cidade, Endereco.cep)
    )
    return list(db.scalars(stmt).all())
