# sdi-front-fornecimentos

Frontend independente para gerenciamento de fornecimentos do Portal B2B.

Enquanto a autenticacao real nao estiver integrada, a tela usa o UUID da empresa fornecedora no campo **Empresa logada** e envia esse valor no header `X-Empresa-Id`.

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
VITE_EMPRESA_ID=
```

Em desenvolvimento, o navegador chama `/api` no proprio Vite e o Vite encaminha para o backend FastAPI. Isso evita problemas de CORS.

## Funcionalidades

- Listar fornecimentos da empresa informada.
- Criar fornecimento.
- Editar preco, produto, endereco e quantidade.
- Atualizar estoque.
- Inativar fornecimento.
- Carregar produtos e enderecos por endpoints auxiliares do backend.
