export type ProdutoOpcao = {
  id: string;
  codigo: string;
  nome: string;
};

export type EnderecoOpcao = {
  id: string;
  empresa_id: string;
  cidade: string;
  estado: string;
  cep: string;
  latitude?: string | null;
  longitude?: string | null;
};

export type Fornecimento = {
  id: string;
  empresa_fornecedor_id: string;
  produto_id: string;
  endereco_origem_id: string;
  preco_unitario: string;
  quantidade_disponivel: string;
  ativo: boolean;
  data_cadastro: string;
  ultima_alteracao?: string | null;
  produto?: ProdutoOpcao | null;
  endereco_origem?: Pick<EnderecoOpcao, "id" | "cidade" | "estado" | "cep"> | null;
};

export type FornecimentoInput = {
  produto_id: string;
  endereco_origem_id: string;
  preco_unitario: number;
  quantidade_disponivel: number;
};

export type EstoqueInput = {
  quantidade_disponivel: number;
};
