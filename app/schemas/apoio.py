import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProdutoOpcao(BaseModel):
    id: uuid.UUID
    codigo: str
    nome: str

    model_config = ConfigDict(from_attributes=True)


class EnderecoOpcao(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID
    cidade: str
    estado: str
    cep: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)
