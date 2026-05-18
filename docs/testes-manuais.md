# Testes manuais - Fornecimentos Service

Este roteiro valida os principais fluxos e regras de erro do `fornecimentos-service` usando Swagger e PostgreSQL.

## Antes de comecar

Rode a API:

```powershell
uvicorn app.main:app --reload
```

Abra o Swagger:

```text
http://localhost:5003/docs
```

Separe estes IDs no banco:

```sql
SELECT e.id AS empresa_fornecedor_id, e.razao_social, e.status
FROM portal_b2b.empresa e
JOIN portal_b2b.empresa_perfil ep ON ep.empresa_id = e.id
JOIN portal_b2b.perfil p ON p.id = ep.perfil_id
WHERE p.nome = 'FORNECEDOR';
```

```sql
SELECT id AS produto_id, codigo, nome, ativo
FROM portal_b2b.produtos_produto;
```

```sql
SELECT id AS endereco_id, empresa_id, cidade, estado, cep
FROM portal_b2b.endereco;
```

## 1. Fluxo feliz - criar fornecimento

Endpoint:

```text
POST /fornecimentos
```

Header:

```text
X-Empresa-Id: ID_DE_EMPRESA_COM_PERFIL_FORNECEDOR
```

Body:

```json
{
  "produto_id": "ID_DE_PRODUTO_ATIVO",
  "endereco_origem_id": "ID_DE_ENDERECO_DA_EMPRESA",
  "preco_unitario": 25.9,
  "quantidade_disponivel": 100
}
```

Resultado esperado:

```text
201 Created
```

## 2. Empresa sem perfil fornecedor

Objetivo: garantir que comprador/transportadora nao consegue cadastrar fornecimento.

Busque uma empresa que nao tenha perfil `FORNECEDOR`:

```sql
SELECT e.id, e.razao_social
FROM portal_b2b.empresa e
WHERE NOT EXISTS (
    SELECT 1
    FROM portal_b2b.empresa_perfil ep
    JOIN portal_b2b.perfil p ON p.id = ep.perfil_id
    WHERE ep.empresa_id = e.id
      AND p.nome = 'FORNECEDOR'
);
```

Use esse ID no header `X-Empresa-Id` e tente criar um fornecimento.

Resultado esperado:

```text
403 Forbidden
Empresa nao possui perfil FORNECEDOR.
```

## 3. Empresa inexistente

Use um UUID aleatorio no header:

```text
X-Empresa-Id: 11111111-1111-1111-1111-111111111111
```

Resultado esperado:

```text
404 Not Found
Empresa ativa nao encontrada.
```

## 4. Produto inexistente

Use uma empresa fornecedora valida no header, mas um UUID aleatorio no `produto_id`:

```json
{
  "produto_id": "22222222-2222-2222-2222-222222222222",
  "endereco_origem_id": "ID_DE_ENDERECO_DA_EMPRESA",
  "preco_unitario": 25.9,
  "quantidade_disponivel": 100
}
```

Resultado esperado:

```text
404 Not Found
Produto ativo nao encontrado.
```

## 5. Produto inativo

No banco, inative temporariamente um produto de teste:

```sql
UPDATE portal_b2b.produtos_produto
SET ativo = false
WHERE id = 'ID_DE_PRODUTO_DE_TESTE';
```

Tente criar fornecimento com esse produto.

Resultado esperado:

```text
404 Not Found
Produto ativo nao encontrado.
```

Depois volte o produto para ativo:

```sql
UPDATE portal_b2b.produtos_produto
SET ativo = true
WHERE id = 'ID_DE_PRODUTO_DE_TESTE';
```

## 6. Endereco de outra empresa

Use uma empresa fornecedora valida no header, mas no body use um `endereco_origem_id` que pertence a outra empresa.

Resultado esperado:

```text
404 Not Found
Endereco de origem nao pertence a empresa fornecedora.
```

## 7. Preco zerado

Body:

```json
{
  "produto_id": "ID_DE_PRODUTO_ATIVO",
  "endereco_origem_id": "ID_DE_ENDERECO_DA_EMPRESA",
  "preco_unitario": 0,
  "quantidade_disponivel": 100
}
```

Resultado esperado:

```text
422 Unprocessable Entity
```

## 8. Quantidade negativa

Body:

```json
{
  "produto_id": "ID_DE_PRODUTO_ATIVO",
  "endereco_origem_id": "ID_DE_ENDERECO_DA_EMPRESA",
  "preco_unitario": 25.9,
  "quantidade_disponivel": -1
}
```

Resultado esperado:

```text
422 Unprocessable Entity
```

## 9. Outra empresa tentando alterar fornecimento

Crie um fornecimento com uma empresa fornecedora valida.

Depois tente atualizar estoque usando outro `X-Empresa-Id`:

```text
PATCH /fornecimentos/{fornecimento_id}/estoque
```

Header:

```text
X-Empresa-Id: ID_DE_OUTRA_EMPRESA
```

Body:

```json
{
  "quantidade_disponivel": 80
}
```

Resultado esperado:

```text
403 Forbidden
Este fornecimento pertence a outra empresa.
```

## 10. Confirmar no banco

Consulte os fornecimentos:

```sql
SELECT *
FROM portal_b2b.fornecimento
ORDER BY data_cadastro DESC;
```

Os testes de erro nao devem criar registros novos, exceto o fluxo feliz.
