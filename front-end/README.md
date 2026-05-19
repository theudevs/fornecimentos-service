# sdi-front-fornecimentos

Frontend independente para gerenciamento de fornecimentos do Portal B2B.

Quando o usuario vem do portal autenticado, a tela le `sessionStorage.portal_b2b_jwt`, envia `Authorization: Bearer <JWT>` e usa a empresa de `sessionStorage.portal_b2b_session`.

## Como rodar

Com o backend FastAPI rodando em `http://127.0.0.1:5003`, execute:

```powershell
npm install
npm run dev
```

Por padrao, o app usa:

```text
VITE_BASE_PATH=/fornecimentos/
VITE_FORNECIMENTO_API_URL=/api/fornecimentos
VITE_FORNECIMENTO_API_TARGET=http://127.0.0.1:5003
```

Em desenvolvimento, o navegador chama `/api` no proprio Vite e o Vite encaminha para o backend FastAPI. Isso evita problemas de CORS.

## Funcionalidades

- Listar fornecimentos da empresa autenticada.
- Criar fornecimento.
- Editar preco, produto, endereco e quantidade.
- Atualizar estoque.
- Inativar fornecimento.
- Carregar produtos e enderecos por endpoints auxiliares do backend.
