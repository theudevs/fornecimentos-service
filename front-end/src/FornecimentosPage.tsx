import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, Boxes, Eye, PackagePlus, Pencil, Power, PowerOff, RefreshCcw, Save, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

import { apoioApi, extractApiError, fornecimentosApi } from "@/api/fornecimentoApi";
import { ThemeToggle } from "@/components/theme-toggle";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getEmpresaIdFromSession, hasAuthToken } from "@/lib/auth";
import type { Fornecimento, FornecimentoInput } from "@/types/fornecimento";

const initialEmpresaId = getEmpresaIdFromSession();

const emptyForm: FornecimentoInput = {
  produto_id: "",
  endereco_origem_id: "",
  preco_unitario: 0,
  quantidade_disponivel: 0,
};

function formatDecimal(value: string | number) {
  const numberValue = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(numberValue)) return String(value);
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(numberValue);
}

function formatCurrency(value: string | number) {
  const numberValue = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(numberValue)) return String(value);
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(numberValue);
}

function getEnderecoLabel(item: Fornecimento) {
  if (!item.endereco_origem) return item.endereco_origem_id;
  return `${item.endereco_origem.cidade}/${item.endereco_origem.estado} - CEP ${item.endereco_origem.cep}`;
}

export default function FornecimentosPage() {
  const queryClient = useQueryClient();
  const empresaId = initialEmpresaId;
  const [apenasAtivos, setApenasAtivos] = useState(true);
  const [form, setForm] = useState<FornecimentoInput>(emptyForm);
  const [editing, setEditing] = useState<Fornecimento | null>(null);
  const [viewing, setViewing] = useState<Fornecimento | null>(null);
  const tokenAvailable = hasAuthToken();

  const produtosQuery = useQuery({
    queryKey: ["apoio", "produtos"],
    queryFn: apoioApi.produtos,
  });

  const enderecosQuery = useQuery({
    queryKey: ["apoio", "enderecos", empresaId],
    queryFn: () => apoioApi.enderecos(empresaId),
    enabled: empresaId.length > 0,
  });

  const fornecimentosQuery = useQuery({
    queryKey: ["fornecimentos", empresaId, apenasAtivos],
    queryFn: () =>
      fornecimentosApi.listar({
        empresa_id: empresaId || undefined,
        apenas_ativos: apenasAtivos,
        limit: 100,
        offset: 0,
      }),
    enabled: empresaId.length > 0,
  });

  const produtosById = useMemo(
    () => new Map((produtosQuery.data ?? []).map((produto) => [produto.id, produto])),
    [produtosQuery.data],
  );

  const saveMutation = useMutation({
    mutationFn: () => {
      if (!empresaId) throw new Error("Informe a empresa logada.");
      if (editing) return fornecimentosApi.atualizar(empresaId, editing.id, form);
      return fornecimentosApi.criar(empresaId, form);
    },
    onSuccess: () => {
      toast.success(editing ? "Fornecimento atualizado" : "Fornecimento criado");
      setForm(emptyForm);
      setEditing(null);
      queryClient.invalidateQueries({ queryKey: ["fornecimentos"] });
    },
    onError: (err) => toast.error(extractApiError(err, "Nao foi possivel salvar o fornecimento")),
  });

  const statusMutation = useMutation({
    mutationFn: (item: Fornecimento) =>
      fornecimentosApi.atualizar(empresaId, item.id, { ativo: !item.ativo }),
    onSuccess: () => {
      toast.success("Status atualizado");
      queryClient.invalidateQueries({ queryKey: ["fornecimentos"] });
    },
    onError: (err) => toast.error(extractApiError(err, "Nao foi possivel atualizar o status")),
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    saveMutation.mutate();
  }

  function startEdit(item: Fornecimento) {
    setEditing(item);
    setForm({
      produto_id: item.produto_id,
      endereco_origem_id: item.endereco_origem_id,
      preco_unitario: Number(item.preco_unitario),
      quantidade_disponivel: Number(item.quantidade_disponivel),
    });
  }

  function toggleStatus(item: Fornecimento) {
    statusMutation.mutate(item);
  }

  function clearForm() {
    setEditing(null);
    setForm(emptyForm);
  }

  const hasEmpresa = empresaId.length > 0;

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,hsl(var(--accent))_0%,hsl(var(--background))_42%,hsl(var(--muted))_100%)]">
      <main className="layout-content max-w-7xl">
        <div className="mb-4 flex flex-col gap-3 border-b bg-card/80 p-4 shadow-card sm:flex-row sm:items-center sm:justify-between">
          <div className="page-header">
            <h1>Fornecimentos</h1>
            <p>Gestao de ofertas de produtos para empresas com perfil fornecedor.</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" onClick={() => fornecimentosQuery.refetch()} title="Atualizar">
              <RefreshCcw className="h-4 w-4" />
            </Button>
            <ThemeToggle />
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
          <section className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <ShieldCheck className="h-4 w-4" />
                  Sessao atual
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  <Badge variant={hasEmpresa ? "default" : "secondary"} className="w-fit">
                    {hasEmpresa ? "Empresa autenticada" : "Sessao nao identificada"}
                  </Badge>
                  {tokenAvailable && (
                    <Badge variant="outline" className="w-fit">
                      JWT detectado
                    </Badge>
                  )}
                </div>
                <div className="flex items-center justify-between rounded-md border px-3 py-2">
                  <Label htmlFor="apenas-ativos" className="text-sm font-medium">
                    Apenas ativos
                  </Label>
                  <Switch id="apenas-ativos" checked={apenasAtivos} onCheckedChange={setApenasAtivos} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <PackagePlus className="h-4 w-4" />
                  {editing ? "Editar fornecimento" : "Novo fornecimento"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form className="space-y-4" onSubmit={handleSubmit}>
                  <div className="space-y-2">
                    <Label>Produto</Label>
                    <Select
                      value={form.produto_id}
                      onValueChange={(value) => setForm((prev) => ({ ...prev, produto_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione um produto" />
                      </SelectTrigger>
                      <SelectContent>
                        {(produtosQuery.data ?? []).map((produto) => (
                          <SelectItem key={produto.id} value={produto.id}>
                            {produto.codigo} - {produto.nome}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Endereco de origem</Label>
                    <Select
                      value={form.endereco_origem_id}
                      disabled={!hasEmpresa}
                      onValueChange={(value) => setForm((prev) => ({ ...prev, endereco_origem_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={hasEmpresa ? "Selecione um endereco" : "Sessao obrigatoria"} />
                      </SelectTrigger>
                      <SelectContent>
                        {(enderecosQuery.data ?? []).map((endereco) => (
                          <SelectItem key={endereco.id} value={endereco.id}>
                            {endereco.cidade}/{endereco.estado} - CEP {endereco.cep}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label htmlFor="preco">Preco unitario</Label>
                      <Input
                        id="preco"
                        type="number"
                        step="0.0001"
                        min="0.0001"
                        value={form.preco_unitario || ""}
                        onChange={(event) => setForm((prev) => ({ ...prev, preco_unitario: Number(event.target.value) }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="quantidade">Quantidade</Label>
                      <Input
                        id="quantidade"
                        type="number"
                        step="0.0001"
                        min="0"
                        value={form.quantidade_disponivel || ""}
                        onChange={(event) =>
                          setForm((prev) => ({ ...prev, quantidade_disponivel: Number(event.target.value) }))
                        }
                      />
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button type="submit" className="flex-1 gap-2" disabled={saveMutation.isPending || !hasEmpresa}>
                      <Save className="h-4 w-4" />
                      Salvar
                    </Button>
                    <Button type="button" variant="outline" onClick={clearForm}>
                      Limpar
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </section>

          <section className="space-y-4">
            {!hasEmpresa && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Sessao nao identificada</AlertTitle>
                <AlertDescription>
                  Acesse pelo portal autenticado para carregar a empresa fornecedora da sessao.
                </AlertDescription>
              </Alert>
            )}

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Boxes className="h-4 w-4" />
                  Fornecimentos cadastrados
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Produto</TableHead>
                        <TableHead>Origem</TableHead>
                        <TableHead className="text-right">Preco</TableHead>
                        <TableHead className="text-right">Qtd.</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="w-[150px] text-right">Acoes</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {(fornecimentosQuery.data ?? []).map((item) => (
                        <TableRow key={item.id}>
                          <TableCell className="min-w-[220px]">
                            <div className="font-medium">{item.produto?.nome ?? produtosById.get(item.produto_id)?.nome ?? item.produto_id}</div>
                            <div className="text-xs text-muted-foreground">
                              {item.produto?.codigo ?? produtosById.get(item.produto_id)?.codigo ?? item.produto_id}
                            </div>
                          </TableCell>
                          <TableCell className="min-w-[220px] text-sm">{getEnderecoLabel(item)}</TableCell>
                          <TableCell className="text-right font-medium">{formatCurrency(item.preco_unitario)}</TableCell>
                          <TableCell className="text-right">{formatDecimal(item.quantidade_disponivel)}</TableCell>
                          <TableCell>
                            {item.ativo ? (
                              <Badge className="border-transparent bg-emerald-100 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-500/15 dark:text-emerald-300 dark:hover:bg-emerald-500/20">
                                Ativo
                              </Badge>
                            ) : (
                              <Badge variant="secondary" className="bg-muted text-muted-foreground">
                                Inativo
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className="flex justify-end gap-1">
                              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setViewing(item)} title="Visualizar">
                                <Eye className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => startEdit(item)} title="Editar">
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                                title={item.ativo ? "Inativar" : "Ativar"}
                                onClick={() => toggleStatus(item)}
                              >
                                {item.ativo ? (
                                  <PowerOff className="h-4 w-4 text-destructive" />
                                ) : (
                                  <Power className="h-4 w-4 text-emerald-600 dark:text-emerald-300" />
                                )}
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                      {hasEmpresa && fornecimentosQuery.data?.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={6} className="h-28 text-center text-sm text-muted-foreground">
                            Nenhum fornecimento encontrado para a empresa informada.
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>

                <Separator className="my-4" />
                <p className="text-xs text-muted-foreground">
                  Produtos e enderecos sao carregados por endpoints auxiliares do backend de fornecimentos enquanto a integracao
                  com os microsservicos donos ainda nao estiver disponivel.
                </p>
              </CardContent>
            </Card>
          </section>
        </div>
      </main>

      <Dialog open={!!viewing} onOpenChange={(open) => !open && setViewing(null)}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Detalhes do fornecimento</DialogTitle>
          </DialogHeader>
          {viewing && (
            <div className="space-y-4 text-sm">
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <p className="text-muted-foreground">Produto</p>
                  <p className="font-medium">{viewing.produto?.nome ?? viewing.produto_id}</p>
                  <p className="text-xs text-muted-foreground">{viewing.produto?.codigo}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Status</p>
                  <p className="font-medium">{viewing.ativo ? "Ativo" : "Inativo"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Preco unitario</p>
                  <p className="font-medium">{formatCurrency(viewing.preco_unitario)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Quantidade disponivel</p>
                  <p className="font-medium">{formatDecimal(viewing.quantidade_disponivel)}</p>
                </div>
                <div className="sm:col-span-2">
                  <p className="text-muted-foreground">Endereco de origem</p>
                  <p className="font-medium">{getEnderecoLabel(viewing)}</p>
                </div>
                <div className="sm:col-span-2">
                  <p className="text-muted-foreground">ID</p>
                  <p className="break-all font-mono text-xs">{viewing.id}</p>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
