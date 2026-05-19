# Contratos de Integracao - Fornecimentos Service

Este documento resume como o `fornecimentos-service` deve ser integrado ao Portal B2B.

## Identificacao

| Item | Valor |
|---|---|
| Servico | `fornecimentos-service` |
| Porta oficial | `5003` |
| Gateway | `/api/fornecimentos/` |
| Health oficial | `/api/fornecimentos/health` |
| Front-end | `fornecimentos-front` |
| Porta do front | `8083` |
| Rota sugerida do front | `/fornecimentos/` |

## Responsabilidade

O servico gerencia ofertas de produtos feitas por empresas com perfil `FORNECEDOR`.

Ele nao cadastra:

- empresas;
- usuarios;
- perfis;
- enderecos;
- produtos.

Esses dados pertencem aos microsservicos de Usuarios/Acesso e Produtos.

## Variaveis de ambiente

```env
SERVICE_NAME=fornecimentos-service
PORT=5003
APP_ENV=production

DATABASE_URL=postgresql://svc_portal_b2b:SENHA_AQUI@136.114.235.212:5432/portal_b2b
DB_SCHEMA=portal_b2b

KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=10.128.0.2:9092,10.128.0.3:9092,10.128.0.4:9092
KAFKA_FAIL_ON_PUBLISH_ERROR=false

AUTH_ENABLED=true
JWT_SECRET=CONFIGURAR_FORA_DO_GIT
JWT_ISSUER=portal-autenticacao
JWT_AUDIENCE=portal-b2b
JWT_CLOCK_SKEW_SECONDS=60
```

Nao versionar `.env` real.

## Endpoints REST

O Gateway remove o prefixo `/api/fornecimentos/`. Portanto, internamente o servico expoe as rotas sem esse prefixo.

| Externo via Gateway | Interno no servico | Descricao |
|---|---|---|
| `GET /api/fornecimentos/health` | `GET /health` | Health check |
| `GET /api/fornecimentos/health/db` | `GET /health/db` | Health do banco |
| `POST /api/fornecimentos/fornecimentos` | `POST /fornecimentos` | Criar fornecimento |
| `GET /api/fornecimentos/fornecimentos` | `GET /fornecimentos` | Listar fornecimentos |
| `GET /api/fornecimentos/fornecimentos/{id}` | `GET /fornecimentos/{id}` | Buscar por ID |
| `PUT /api/fornecimentos/fornecimentos/{id}` | `PUT /fornecimentos/{id}` | Atualizar fornecimento |
| `PATCH /api/fornecimentos/fornecimentos/{id}/estoque` | `PATCH /fornecimentos/{id}/estoque` | Atualizar estoque |
| `DELETE /api/fornecimentos/fornecimentos/{id}` | `DELETE /fornecimentos/{id}` | Inativar fornecimento |
| `GET /api/fornecimentos/empresas/{id}/fornecimentos` | `GET /empresas/{id}/fornecimentos` | Listar por empresa |

## Endpoints auxiliares temporarios

Enquanto a integracao com Produtos e Usuarios/Acesso nao estiver concluida, o frontend usa:

| Externo via Gateway | Interno no servico | Uso |
|---|---|---|
| `GET /api/fornecimentos/apoio/produtos` | `GET /apoio/produtos` | Select de produtos ativos |
| `GET /api/fornecimentos/apoio/empresas/{empresa_id}/enderecos` | `GET /apoio/empresas/{empresa_id}/enderecos` | Select de enderecos da empresa |

Esses endpoints sao auxiliares. No desenho final, os dados devem vir dos servicos donos:

- produtos ativos: `produtos-service`;
- enderecos da empresa: `usuarios-service`.

## Autenticacao

Estado implementado:

- Frontend envia `Authorization: Bearer <JWT>` quando encontra `sessionStorage.portal_b2b_jwt`.
- Frontend preenche a empresa logada a partir de `sessionStorage.portal_b2b_session`.
- Backend valida o JWT emitido pelo `usuarios-service`.
- Backend extrai a empresa pela claim `empresa_id`.
- Backend aceita tokens com `role` ausente ou contendo `FORNECEDOR`; se vierem roles e `FORNECEDOR` nao existir, retorna `403`.
- Backend ainda confirma no banco se a empresa existe, esta ativa e possui perfil `FORNECEDOR`.

Modo local:

- Com `AUTH_ENABLED=false`, o backend aceita o header `X-Empresa-Id` para testes no Swagger e no frontend local.
- Com `AUTH_ENABLED=true`, `Authorization: Bearer <JWT>` e obrigatorio.
- A interface React nao exibe campo manual de empresa; ela usa a sessao/JWT do portal.

Claims esperadas do JWT:

```json
{
  "sub": "uuid-do-usuario",
  "email": "usuario@empresa.com",
  "name": "Nome Usuario",
  "empresa_id": "uuid-da-empresa",
  "role": ["FORNECEDOR"],
  "iss": "portal-autenticacao",
  "aud": "portal-b2b"
}
```

Nao versionar `JWT_SECRET` real.

## Eventos Kafka publicados

O nome do topico deve ser exatamente igual ao `eventType`.

### fornecimento_criado

Topico:

```text
fornecimento_criado
```

Envelope:

```json
{
  "eventId": "uuid",
  "eventType": "fornecimento_criado",
  "eventVersion": "1.0",
  "timestamp": "2026-05-18T12:00:00Z",
  "source": "fornecimentos-service",
  "correlationId": "uuid",
  "payload": {
    "idFornecimento": "uuid",
    "idEmpresaFornecedor": "uuid",
    "idProduto": "uuid",
    "idEnderecoOrigem": "uuid",
    "precoUnitario": "25.9000",
    "quantidadeDisponivel": "100.0000"
  }
}
```

### estoque_atualizado

Topico:

```text
estoque_atualizado
```

Envelope:

```json
{
  "eventId": "uuid",
  "eventType": "estoque_atualizado",
  "eventVersion": "1.0",
  "timestamp": "2026-05-18T12:00:00Z",
  "source": "fornecimentos-service",
  "correlationId": "uuid",
  "payload": {
    "idFornecimento": "uuid",
    "idEmpresaFornecedor": "uuid",
    "idProduto": "uuid",
    "quantidadeAnterior": "100.0000",
    "quantidadeDisponivel": "80.0000"
  }
}
```

## Eventos consumidos

Nenhum consumo obrigatorio implementado nesta versao.

Possibilidades futuras:

- `produto_cadastrado`;
- `empresa_cadastrada`.

## Tabelas usadas

Consulta:

- `portal_b2b.empresa`
- `portal_b2b.perfil`
- `portal_b2b.empresa_perfil`
- `portal_b2b.endereco`
- `portal_b2b.produtos_produto`

Gerenciada pelo servico:

- `portal_b2b.fornecimento`

O servico nao faz DDL nem cria tabelas automaticamente.

## Checklist para deploy

- [ ] `Dockerfile` existe na raiz.
- [ ] `docker-compose.yml` existe na raiz.
- [ ] `.env.example` nao contem segredo real.
- [ ] Backend escuta em `0.0.0.0:5003`.
- [ ] Compose publica `5003:5003`.
- [ ] Front publica `8083:80`.
- [ ] Ambos usam rede `portal-b2b-network`.
- [ ] `GET /health` retorna 200.
- [ ] Kafka usa `10.128.0.2:9092,10.128.0.3:9092,10.128.0.4:9092`.
- [ ] Topicos publicados sao `fornecimento_criado` e `estoque_atualizado`.
