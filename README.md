# Portal B2B - Fornecimentos Service

Microsservico em FastAPI responsavel por cadastrar e manter **fornecimentos**.

## Responsabilidade deste servico

- Criar fornecimento para uma empresa fornecedora.
- Listar fornecimentos.
- Buscar fornecimento por ID.
- Atualizar preco, produto, endereco de origem, estoque e status.
- Inativar fornecimento sem apagar fisicamente.
- Publicar eventos Kafka quando um fornecimento for criado, estoque for alterado ou fornecimento for inativado.

## Tabelas usadas

Tabelas apenas consultadas:

- `portal_b2b.empresa`
- `portal_b2b.perfil`
- `portal_b2b.empresa_perfil`
- `portal_b2b.endereco`
- `portal_b2b.produtos_produto`

Tabela gerenciada por este servico:

- `portal_b2b.fornecimento`

O servico nao cria tabelas. O DDL fica com a equipe de banco de dados.

## Como rodar

Instale Python 3.11 ou superior. Depois, dentro da pasta `fornecimentos-service`:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Abra o Swagger:

```text
http://localhost:8000/docs
```

## Header obrigatorio nos endpoints de escrita

Como o login pertence a outro microsservico, os endpoints que criam ou alteram dados recebem a empresa autenticada via header:

```text
X-Empresa-Id: UUID_DA_EMPRESA
```

Depois, quando a equipe de Usuarios/Acesso entregar autenticacao com JWT, esse header pode ser substituido pelo ID vindo do token.

## Endpoints

```text
GET    /health
GET    /health/db
POST   /fornecimentos
GET    /fornecimentos
GET    /fornecimentos/{fornecimento_id}
GET    /empresas/{empresa_id}/fornecimentos
PUT    /fornecimentos/{fornecimento_id}
PATCH  /fornecimentos/{fornecimento_id}/estoque
DELETE /fornecimentos/{fornecimento_id}
```

## Regras implementadas

- A empresa precisa existir e estar com `status = 'ATIVO'`.
- A empresa precisa possuir perfil `FORNECEDOR`.
- O produto precisa existir e estar ativo.
- O endereco de origem precisa pertencer a empresa fornecedora.
- `preco_unitario` precisa ser maior que zero.
- `quantidade_disponivel` precisa ser maior ou igual a zero.
- Exclusao e logica: `ativo = false`.

## Eventos Kafka

O Kafka fica desligado por padrao para facilitar os primeiros testes:

```env
KAFKA_ENABLED=false
```

Quando o ambiente Kafka da turma estiver disponivel, configure:

```env
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_FORNECIMENTOS=portal-b2b.fornecimentos
```

Eventos publicados:

- `fornecimento_criado`
- `estoque_atualizado`
- `fornecimento_inativado`

Formato:

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
