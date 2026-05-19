import axios, { AxiosError } from "axios";
import type {
  EnderecoOpcao,
  EstoqueInput,
  Fornecimento,
  FornecimentoInput,
  ProdutoOpcao,
} from "@/types/fornecimento";
import { getAuthToken } from "@/lib/auth";

const baseURL =
  (import.meta.env.VITE_FORNECIMENTO_API_URL as string | undefined)?.trim() ||
  "/api/fornecimentos";

export const fornecimentoHttp = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

fornecimentoHttp.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export function extractApiError(err: unknown, fallback = "Erro inesperado"): string {
  if (err instanceof AxiosError) {
    const data = err.response?.data as { detail?: unknown; mensagem?: string; erros?: string[] } | undefined;
    if (Array.isArray(data?.erros) && data.erros.length > 0) return data.erros.join(", ");
    if (typeof data?.mensagem === "string") return data.mensagem;
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail)) return data.detail.map((item) => item?.msg ?? "Erro de validacao").join(", ");
    return err.message || fallback;
  }
  if (err instanceof Error) return err.message;
  return fallback;
}

function buildParams(params: Record<string, unknown>) {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    out[key] = value;
  }
  return out;
}

function empresaHeaders(empresaId: string) {
  return { "X-Empresa-Id": empresaId };
}

export const apoioApi = {
  produtos: () => fornecimentoHttp.get<ProdutoOpcao[]>("/apoio/produtos").then((res) => res.data),
  enderecos: (empresaId: string) =>
    fornecimentoHttp.get<EnderecoOpcao[]>(`/apoio/empresas/${empresaId}/enderecos`).then((res) => res.data),
};

export const fornecimentosApi = {
  listar: (params: { empresa_id?: string; produto_id?: string; apenas_ativos?: boolean; limit?: number; offset?: number }) =>
    fornecimentoHttp
      .get<Fornecimento[]>("/fornecimentos", { params: buildParams(params) })
      .then((res) => res.data),
  criar: (empresaId: string, input: FornecimentoInput) =>
    fornecimentoHttp
      .post<Fornecimento>("/fornecimentos", input, { headers: empresaHeaders(empresaId) })
      .then((res) => res.data),
  atualizar: (empresaId: string, id: string, input: Partial<FornecimentoInput> & { ativo?: boolean }) =>
    fornecimentoHttp
      .put<Fornecimento>(`/fornecimentos/${id}`, input, { headers: empresaHeaders(empresaId) })
      .then((res) => res.data),
  atualizarEstoque: (empresaId: string, id: string, input: EstoqueInput) =>
    fornecimentoHttp
      .patch<Fornecimento>(`/fornecimentos/${id}/estoque`, input, { headers: empresaHeaders(empresaId) })
      .then((res) => res.data),
  inativar: (empresaId: string, id: string) =>
    fornecimentoHttp.delete(`/fornecimentos/${id}`, { headers: empresaHeaders(empresaId) }),
};
