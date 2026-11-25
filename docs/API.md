# API

Swagger interativo: http://localhost:8000/docs

| Método | Rota | Uso |
|---|---|---|
| GET | /cartoes/ | Modalidades |
| GET | /lojas/parceiras | Busca por cep, modalidade, busca, latitude, longitude, pagina e limite |
| GET | /lojas/programas | Programas ativos |
| POST | /lojas/redes | Criar rede (x-admin-token) |
| POST | /lojas/programas | Criar programa (x-admin-token) |
| POST | /lojas/parceiras | Criar unidade (x-admin-token) |
| PUT | /lojas/parceiras/{id}/programa | Vincular programa e coordenadas (x-admin-token) |
| POST | /solicitacoes/ | Captação e código privado |
| POST | /solicitacoes/consultar | CPF e código privado |
| GET | /solicitacoes/{id} | Protocolo, CPF e código |
| POST | /ofertas/interesse | Consentimento, CPF, e-mail, código e protocolo |
| GET | /ofertas/confirmar | Confirmação por token |
| POST | /parceiros/contas | Criar conta (x-admin-token) |
| POST | /parceiros/autenticar | Login |
| GET/POST | /parceiros/eu/contribuidores | Gestão com Bearer token |

409: duplicidade ou conflito cadastral. 400: regra de negócio inválida. 422: dados fora do schema. 429: limite de requisições. Não use dados reais no protótipo. As consultas de usuários exigem token administrativo.
