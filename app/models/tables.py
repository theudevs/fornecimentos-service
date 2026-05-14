import uuid
from decimal import Decimal

from sqlalchemy import Boolean, CHAR, DECIMAL, ForeignKey, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Empresa(Base):
    __tablename__ = "empresa"
    __table_args__ = {"schema": "portal_b2b"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    razao_social: Mapped[str] = mapped_column(String(255))
    nome_fantasia: Mapped[str | None] = mapped_column(String(255))
    cnpj: Mapped[str] = mapped_column(CHAR(14))
    email: Mapped[str] = mapped_column(String(150))
    telefone: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    data_cadastro = mapped_column(TIMESTAMP(timezone=True))
    ultima_alteracao = mapped_column(TIMESTAMP(timezone=True))


class Perfil(Base):
    __tablename__ = "perfil"
    __table_args__ = {"schema": "portal_b2b"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    nome: Mapped[str] = mapped_column(String(50))


class EmpresaPerfil(Base):
    __tablename__ = "empresa_perfil"
    __table_args__ = {"schema": "portal_b2b"}

    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portal_b2b.empresa.id"),
        primary_key=True,
    )
    perfil_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portal_b2b.perfil.id"),
        primary_key=True,
    )


class Endereco(Base):
    __tablename__ = "endereco"
    __table_args__ = {"schema": "portal_b2b"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portal_b2b.empresa.id"))
    cidade: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(CHAR(2))
    cep: Mapped[str] = mapped_column(CHAR(8))
    latitude: Mapped[Decimal | None] = mapped_column(DECIMAL(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(DECIMAL(9, 6))


class Produto(Base):
    __tablename__ = "produtos_produto"
    __table_args__ = {"schema": "portal_b2b"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    transporte_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    categoria_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    unidade_medida_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    codigo: Mapped[str] = mapped_column(String(60))
    nome: Mapped[str] = mapped_column(String(150))
    descricao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean)
    data_cadastro = mapped_column(TIMESTAMP(timezone=True))
    ultima_alteracao = mapped_column(TIMESTAMP(timezone=True))


class Fornecimento(Base):
    __tablename__ = "fornecimento"
    __table_args__ = {"schema": "portal_b2b"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    empresa_fornecedor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portal_b2b.empresa.id"),
    )
    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portal_b2b.produtos_produto.id"))
    endereco_origem_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portal_b2b.endereco.id"))
    preco_unitario: Mapped[Decimal] = mapped_column(DECIMAL(18, 4))
    quantidade_disponivel: Mapped[Decimal] = mapped_column(DECIMAL(18, 4))
    ativo: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    data_cadastro = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    ultima_alteracao = mapped_column(TIMESTAMP(timezone=True))

    empresa = relationship("Empresa")
    produto = relationship("Produto")
    endereco_origem = relationship("Endereco")
