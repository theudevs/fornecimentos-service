import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FornecimentoCreate(BaseModel):
    produto_id: uuid.UUID
    endereco_origem_id: uuid.UUID
    preco_unitario: Decimal = Field(gt=0, decimal_places=4)
    quantidade_disponivel: Decimal = Field(ge=0, decimal_places=4)


class FornecimentoUpdate(BaseModel):
    produto_id: uuid.UUID | None = None
    endereco_origem_id: uuid.UUID | None = None
    preco_unitario: Decimal | None = Field(default=None, gt=0, decimal_places=4)
    quantidade_disponivel: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    ativo: bool | None = None


class EstoqueUpdate(BaseModel):
    quantidade_disponivel: Decimal = Field(ge=0, decimal_places=4)


class ProdutoResumo(BaseModel):
    id: uuid.UUID
    codigo: str
    nome: str

    model_config = ConfigDict(from_attributes=True)


class EnderecoResumo(BaseModel):
    id: uuid.UUID
    cidade: str
    estado: str
    cep: str

    model_config = ConfigDict(from_attributes=True)


class FornecimentoResponse(BaseModel):
    id: uuid.UUID
    empresa_fornecedor_id: uuid.UUID
    produto_id: uuid.UUID
    endereco_origem_id: uuid.UUID
    preco_unitario: Decimal
    quantidade_disponivel: Decimal
    ativo: bool
    data_cadastro: datetime
    ultima_alteracao: datetime | None
    produto: ProdutoResumo | None = None
    endereco_origem: EnderecoResumo | None = None

    model_config = ConfigDict(from_attributes=True)
