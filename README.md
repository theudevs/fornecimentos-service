# Portal B2B - Fornecimentos Service

Microsservico em FastAPI responsavel pelo cadastro e manutencao de **fornecimentos** no Portal B2B.

Este servico nao cadastra empresas, usuarios, perfis, enderecos ou produtos; ele apenas registra quais produtos uma empresa fornecedora oferece, com preco, quantidade e endereco de origem.

## Responsabilidade

Este servico e responsavel por:

- Criar fornecimentos para empresas com perfil `FORNECEDOR`.
- Listar fornecimentos ativos ou todos os fornecimentos.
- Buscar fornecimento por ID.
- Listar fornecimentos de uma empresa.
- Atualizar preco, produto, endereco de origem, quantidade e status.
- Atualizar estoque/quantidade disponivel.
- Inativar fornecimento por exclusao logica.
- Publicar eventos Kafka previstos para fornecimentos.

Este servico nao e responsavel por:

- Cadastro de empresa.
- Login/autenticacao.
- Cadastro de perfis.
- Cadastro de enderecos.
- Cadastro de produtos.
- Processo de negociacao, pedidos ou frete.

## Dependencias De Outros Servicos

### Usuarios/Acesso

O servico de Usuarios/Acesso deve fornecer:

- Empresa autenticada.
- Perfil ativo da empresa.
- Cadastro e manutencao de enderecos.

Enquanto a autenticacao real nao estiver integrada, os endpoints de escrita usam o header:

```text
X-Empresa-Id: UUID_DA_EMPRESA
```

Futuramente, esse valor deve vir do JWT ou mecanismo oficial de autenticacao.

### Produtos

O servico de Produtos deve fornecer:

- Catalogo de produtos ativos.
- Identificador do produto (`produto_id`) usado no fornecimento.

O produto e um catalogo compartilhado do portal. O fornecimento representa a oferta de uma empresa para um produto do catalogo.

## Banco De Dados

O banco oficial e PostgreSQL, usando o schema:

```text
portal_b2b
```

Tabelas apenas consultadas:

- `portal_b2b.empresa`
- `portal_b2b.perfil`
- `portal_b2b.empresa_perfil`
- `portal_b2b.endereco`
- `portal_b2b.produtos_produto`

Tabela gerenciada por este servico:

- `portal_b2b.fornecimento`

Importante: este microsservico **nao cria nem altera tabelas**. O DDL pertence a equipe de Banco/Integracao.

## Tecnologias

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Uvicorn
- Confluent Kafka Producer

## Como Rodar

Crie o ambiente virtual:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Crie o arquivo `.env`:

```powershell
Copy-Item .env.example .env
```

Configure a conexao no `.env`:

```env
SERVICE_NAME=fornecimentos-service
PORT=5003
APP_ENV=local
DATABASE_URL=postgresql://svc_portal_b2b:SENHA_AQUI@136.114.235.212:5432/portal_b2b
DB_SCHEMA=portal_b2b
KAFKA_ENABLED=false
KAFKA_BOOTSTRAP_SERVERS=10.128.0.2:9092,10.128.0.3:9092,10.128.0.4:9092
KAFKA_FAIL_ON_PUBLISH_ERROR=false
```

Rode a API:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 5003 --reload
```

Abra o Swagger:

```text
http://localhost:5003/docs
```

No ambiente de integracao, o acesso externo oficial sera:

```text
http://34.8.17.245/api/fornecimentos/health
```

## Health Check

### GET /health

Verifica se a aplicacao esta respondendo.

Resposta esperada:

```json
{
  "status": "ok",
  "service": "fornecimentos-service"
}
```

### GET /health/db

Verifica se a aplicacao consegue conectar no banco.

Resposta esperada:

```json
{
  "status": "ok",
  "database": "connected"
}
```

## Endpoints

```text
GET    /health
GET    /health/db
GET    /apoio/produtos
GET    /apoio/empresas/{empresa_id}/enderecos
POST   /fornecimentos
GET    /fornecimentos
GET    /fornecimentos/{fornecimento_id}
GET    /empresas/{empresa_id}/fornecimentos
PUT    /fornecimentos/{fornecimento_id}
PATCH  /fornecimentos/{fornecimento_id}/estoque
DELETE /fornecimentos/{fornecimento_id}
```

Os endpoints `/apoio/*` existem para desenvolvimento e demonstracao do frontend enquanto a integracao com os microsservicos de Produtos e Usuarios/Acesso ainda nao estiver disponivel.

## Criar Fornecimento

### POST /fornecimentos

Header:

```text
X-Empresa-Id: UUID_DA_EMPRESA_FORNECEDORA
```

Body:

```json
{
  "produto_id": "65d2909c-622c-4b99-863b-6d85ee3f57b0",
  "endereco_origem_id": "e0620eb7-5633-4a5f-987f-a9eb2cc589ed",
  "preco_unitario": 25.9,
  "quantidade_disponivel": 100
}
```

Resposta `201 Created`:

```json
{
  "id": "f4a52aa3-60dc-4190-b22a-27464b165caa",
  "empresa_fornecedor_id": "01bee500-3565-4fe3-8951-75b0bee02b3b",
  "produto_id": "65d2909c-622c-4b99-863b-6d85ee3f57b0",
  "endereco_origem_id": "e0620eb7-5633-4a5f-987f-a9eb2cc589ed",
  "preco_unitario": "25.9000",
  "quantidade_disponivel": "100.0000",
  "ativo": true,
  "data_cadastro": "2026-05-14T08:32:12.374105-03:00",
  "ultima_alteracao": null,
  "produto": {
    "id": "65d2909c-622c-4b99-863b-6d85ee3f57b0",
    "codigo": "ARROZ-T1-5KG",
    "nome": "Arroz Tipo 1 - 5kg"
  },
  "endereco_origem": {
    "id": "e0620eb7-5633-4a5f-987f-a9eb2cc589ed",
    "cidade": "Sao Paulo",
    "estado": "SP",
    "cep": "01001000"
  }
}
```

## Listar Fornecimentos

### GET /fornecimentos

Parametros opcionais:

```text
empresa_id
produto_id
apenas_ativos
limit
offset
```

Exemplo:

```text
GET /fornecimentos?apenas_ativos=true&limit=50&offset=0
```

## Buscar Fornecimento

### GET /fornecimentos/{fornecimento_id}

Retorna um fornecimento especifico pelo ID.

## Listar Fornecimentos Por Empresa

### GET /empresas/{empresa_id}/fornecimentos

Retorna os fornecimentos cadastrados para uma empresa.

## Atualizar Fornecimento

### PUT /fornecimentos/{fornecimento_id}

Header:

```text
X-Empresa-Id: UUID_DA_EMPRESA_FORNECEDORA
```

Body exemplo:

```json
{
  "preco_unitario": 23.5,
  "quantidade_disponivel": 80
}
```

## Atualizar Estoque

### PATCH /fornecimentos/{fornecimento_id}/estoque

Header:

```text
X-Empresa-Id: UUID_DA_EMPRESA_FORNECEDORA
```

Body:

```json
{
  "quantidade_disponivel": 80
}
```

## Inativar Fornecimento

### DELETE /fornecimentos/{fornecimento_id}

Header:

```text
X-Empresa-Id: UUID_DA_EMPRESA_FORNECEDORA
```

Resposta esperada:

```text
204 No Content
```

A exclusao e logica. O registro permanece no banco com:

```text
ativo = false
```

## Regras De Negocio Implementadas

- Empresa precisa existir.
- Empresa precisa estar com `status = 'ATIVO'`.
- Empresa precisa possuir perfil `FORNECEDOR`.
- Produto precisa existir.
- Produto precisa estar ativo.
- Endereco de origem precisa pertencer a empresa fornecedora.
- `preco_unitario` precisa ser maior que zero.
- `quantidade_disponivel` precisa ser maior ou igual a zero.
- Apenas a propria empresa fornecedora pode alterar ou inativar seu fornecimento.
- Inativacao nao remove fisicamente o registro.

## Principais Erros

### Empresa inexistente ou inativa

```text
404 Not Found
Empresa ativa nao encontrada.
```

### Empresa sem perfil fornecedor

```text
403 Forbidden
Empresa nao possui perfil FORNECEDOR.
```

### Produto inexistente ou inativo

```text
404 Not Found
Produto ativo nao encontrado.
```

### Endereco de outra empresa

```text
404 Not Found
Endereco de origem nao pertence a empresa fornecedora.
```

### Preco ou quantidade invalida

```text
422 Unprocessable Entity
```

## Eventos Kafka

O Kafka pode ficar desligado durante o desenvolvimento local:

```env
KAFKA_ENABLED=false
```

Quando o ambiente Kafka estiver disponivel:

```env
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=10.128.0.2:9092,10.128.0.3:9092,10.128.0.4:9092
```

Eventos publicados:

- `fornecimento_criado`
- `estoque_atualizado`

Formato padrao:

```json
{
  "eventId": "uuid",
  "eventType": "fornecimento_criado",
  "eventVersion": "1.0",
  "timestamp": "2026-05-14T12:00:00Z",
  "source": "fornecimentos-service",
  "correlationId": "uuid",
  "payload": {}
}
```

O nome do topico Kafka publicado e sempre igual ao `eventType`, conforme o padrao oficial da infraestrutura.

### Evento fornecimento_criado

Payload:

```json
{
  "idFornecimento": "uuid",
  "idEmpresaFornecedor": "uuid",
  "idProduto": "uuid",
  "idEnderecoOrigem": "uuid",
  "precoUnitario": "25.9000",
  "quantidadeDisponivel": "100.0000"
}
```

### Evento estoque_atualizado

Payload:

```json
{
  "idFornecimento": "uuid",
  "idEmpresaFornecedor": "uuid",
  "idProduto": "uuid",
  "quantidadeAnterior": "100.0000",
  "quantidadeDisponivel": "80.0000"
}
```

## Testes Manuais

O roteiro de testes de sucesso e erro esta em:

```text
docs/testes-manuais.md
```

## Frontend

O frontend React fica em:

```text
front-end/
```

Ele usa React, Vite, TypeScript, Tailwind, shadcn/ui, axios e react-query, seguindo o padrao visual do frontend do microsservico de Produtos.

Para rodar o backend:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 5003 --reload
```

Para rodar o frontend:

```powershell
cd front-end
npm install
npm run dev
```

Abra:

```text
http://127.0.0.1:8083/fornecimentos/
```

Enquanto a autenticacao real nao estiver pronta, informe manualmente o UUID da empresa fornecedora no campo **Empresa logada**. Esse valor e enviado para a API no header `X-Empresa-Id`.

## Docker

O repositorio esta preparado para deploy na infraestrutura oficial com:

```text
Dockerfile
docker-compose.yml
.env.example
```

O compose sobe:

- `fornecimentos-service` na porta oficial `5003`.
- `fornecimentos-front` na porta sugerida `8083`.
- ambos na rede externa `portal-b2b-network`.

Para executar em ambiente com a rede da infra criada:

```bash
cp .env.example .env
docker compose up -d --build
```
