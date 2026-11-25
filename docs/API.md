# API

Swagger interativo: http://localhost:8000/docs

| Método | Rota | Uso |
|---|---|---|
| GET | /cartoes/ | Modalidades |
| GET | /lojas/parceiras | Busca por CEP, modalidade, texto e paginação |
| POST | /lojas/buscar | Busca com localização no corpo da requisição |
| GET | /lojas/programas | Programas ativos |
| GET | /lojas/redes | Redes ativas |
| POST | /lojas/redes | Criar rede (x-admin-token) |
| POST | /lojas/programas | Criar programa (x-admin-token) |
| POST | /lojas/parceiras | Criar unidade (x-admin-token) |
| PUT | /lojas/parceiras/{id}/programa | Adicionar programa ou coordenadas (x-admin-token) |
| POST | /solicitacoes/ | Captação; loja e programa para cartão de loja; código privado |
| POST | /solicitacoes/consultar | CPF e código privado |
| POST | /solicitacoes/{id}/codigo | Recuperar código após verificação de identidade (admin) |
| GET | /solicitacoes/{id} | Protocolo; cabeçalhos X-CPF e X-Codigo-Consulta |
| POST | /ofertas/interesse | Consentimento, CPF, e-mail, código e protocolo |
| GET | /ofertas/confirmar | Confirmação por token |
| POST | /parceiros/contas | Criar conta (x-admin-token) |
| POST | /parceiros/autenticar | Login |
| GET/POST | /parceiros/eu/contribuidores | Gestão com Bearer token |

409: duplicidade ou conflito cadastral. 400: regra de negócio inválida. 422: dados fora do schema. 429: limite de requisições. Não use dados reais no protótipo. As consultas de usuários exigem token administrativo.
