# Sprint 1 - Alterações realizadas

Este arquivo registra o que foi ajustado no projeto para transformar a primeira Sprint em uma entrega demonstrável de ponta a ponta, sem antecipar as regras principais planejadas para as Sprints 2 e 3.

## Objetivo da entrega

A Sprint 1 agora permite que uma pessoa:

1. acesse uma landing page responsiva;
2. escolha entre Cartão DM, Cartão Loja Física e Cartão Loja Digital;
3. informe nome, CPF, e-mail, telefone e CEP;
4. consulte lojas parceiras do mesmo estado do CEP quando escolher Cartão Loja Física;
5. escolha uma das lojas retornadas;
6. envie a solicitação para a API;
7. tenha seus dados gravados no banco;
8. receba um número de solicitação e o status inicial `EM_ANALISE`.

Esse fluxo cobre as quatro User Stories previstas no Product Backlog para a Sprint 1.

## Principais correções de funcionamento

### Docker

O `docker-compose.yml` tinha uma incompatibilidade entre a porta exposta pelo Nginx do frontend e a porta usada pelo Compose. O frontend agora é publicado corretamente em `http://localhost:5173`.

Também foram adicionados valores padrão para o MySQL. Assim, o projeto pode ser iniciado sem criar um `.env` obrigatoriamente.

Serviços:

- MySQL: `localhost:3306`
- API FastAPI: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

### Comunicação frontend e backend

Foi habilitado CORS na API para que a landing page consiga consumir o backend durante a execução local e em demonstrações na rede da faculdade.

O frontend agora chama a API usando o mesmo host em que a página foi aberta e a porta `8000`.

## Backend

### Cartões

Foi criado o endpoint:

`GET /cartoes/`

A base inicial contém:

- Cartão DM
- Cartão Loja Física
- Cartão Loja Digital

Os dados são inseridos automaticamente quando a aplicação inicia pela primeira vez.

### Estabelecimentos parceiros

Foi criada a tabela `estabelecimentos_parceiros` com:

- id
- nome
- estado
- cidade
- endereço
- CEP
- ativo

Também foram adicionadas lojas de demonstração em alguns estados para permitir a apresentação da funcionalidade.

Foi criado o endpoint:

`GET /lojas/parceiras?cep=12210000`

O serviço tenta identificar o estado pelo ViaCEP. Caso a consulta externa não esteja disponível, existe uma identificação local por faixa de CEP para manter a demonstração funcionando.

O endpoint retorna apenas lojas do estado identificado pelo CEP.

### Solicitações

Foi criada a tabela `solicitacoes` com:

- id
- usuario_id
- tipo_cartao
- loja_id
- status
- criado_em

Foi criado o endpoint:

`POST /solicitacoes/`

Ele valida os dados, cria ou reaproveita o cadastro do cliente e registra a solicitação.

Na Sprint 1, o status inicial é `EM_ANALISE`.

Para Cartão Loja Física, o backend também valida se a loja escolhida pertence ao mesmo estado do CEP informado. Dessa forma, a regra não fica protegida apenas pelo frontend.

Também foi criado:

`GET /solicitacoes/{id}`

### Usuários

O cadastro foi ajustado para receber somente informações que o cliente deve preencher.

O campo `colaborador_dm` não é mais informado pelo usuário. Nesta Sprint ele começa como `false`, deixando a identificação real do colaborador para a Sprint 2.

Foram mantidos os endpoints existentes de cadastro e consulta de usuários.

### Dados iniciais

Foi adicionado `backend/app/seed.py` para cadastrar cartões e lojas de demonstração sem precisar inserir registros manualmente no MySQL antes da apresentação.

### Código antigo de User

O arquivo `backend/User/UserEntity.py`, que possuía definição inválida de coluna de CPF e erro no parâmetro `nullable`, foi corrigido para não deixar código quebrado no repositório.

## Frontend

A estrutura vazia da landing page foi completada com:

- header responsivo;
- hero com chamada para ação;
- seção de benefícios;
- seção explicando o fluxo;
- formulário em três passos;
- FAQ;
- footer;
- responsividade para celular;
- máscaras simples de CPF, telefone e CEP;
- mensagens de erro da API;
- estado de carregamento durante o envio.

### Passo 1 - Escolha do cartão

O usuário consegue selecionar uma das três opções disponíveis e avançar somente depois da escolha.

### Passo 2 - Dados pessoais

O formulário coleta:

- nome completo;
- CPF;
- telefone;
- e-mail;
- CEP.

Se a opção for Cartão Loja Física, aparece também a busca de lojas por CEP. O usuário precisa escolher uma loja antes de enviar.

### Passo 3 - Resultado

Depois do envio, são exibidos:

- status `Em análise`;
- número da solicitação;
- cartão escolhido;
- loja escolhida, quando existir.

Também existe opção para iniciar uma nova solicitação.

## Arquivos adicionados

Backend:

- `backend/app/models/application.py`
- `backend/app/models/partner_store.py`
- `backend/app/schemas/application.py`
- `backend/app/schemas/card.py`
- `backend/app/schemas/partner_store.py`
- `backend/app/controllers/application_controller.py`
- `backend/app/controllers/card_controller.py`
- `backend/app/controllers/store_controller.py`
- `backend/app/services/cep_service.py`
- `backend/app/seed.py`

Projeto e documentação:

- `.env.example`
- `.gitignore`
- `SPRINT1_ALTERACOES.md`
- `docs/MANUAL_INSTALACAO.md`
- `docs/MANUAL_USUARIO_SPRINT1.md`

## Arquivos alterados

- `docker-compose.yml`
- `backend/app/database.py`
- `backend/app/main.py`
- `backend/app/controllers/user_controller.py`
- `backend/app/schemas/user.py`
- `backend/User/UserEntity.py`
- `frontend/index.html`
- `frontend/css/base.css`
- `frontend/css/header.css`
- `frontend/css/hero.css`
- `frontend/css/beneficios.css`
- `frontend/css/prova-social.css`
- `frontend/css/formulario.css`
- `frontend/css/footer.css`
- `frontend/js/main.js`
- `frontend/js/stepper.js`
- `frontend/js/passo1-escolha-cartao.js`
- `frontend/js/passo2-formulario.js`
- `frontend/js/passo3-resultado.js`
- `docs/sprints/sprint-1/README.md`
- `README.md`

## Como executar

Na raiz do projeto:

```bash
docker compose up --build
```

Depois, abrir:

`http://localhost:5173`

Para encerrar:

```bash
docker compose down
```

Para apagar também o banco local criado pelo Docker:

```bash
docker compose down -v
```

## Roteiro curto para demonstrar a Sprint 1

1. Abrir a landing page.
2. Clicar em `Começar solicitação`.
3. Selecionar `Cartão Loja Física`.
4. Preencher os dados.
5. Usar um CEP de São José dos Campos, por exemplo `12210-000`.
6. Clicar em `Buscar lojas`.
7. Mostrar que aparecem apenas lojas cadastradas em SP.
8. Escolher uma loja.
9. Enviar a solicitação.
10. Mostrar o status `Em análise` e o número gerado.
11. Abrir `http://localhost:8000/docs` para demonstrar a API.

Também vale repetir o fluxo com `Cartão DM` para mostrar que ele não exige escolha de loja.

## O que foi deixado propositalmente para as próximas Sprints

### Sprint 2

Não foi implementada a identificação real de colaboradores DM nem suas regras automáticas de aprovação ou reprovação. Também não foi concluído o comportamento específico do Cartão Loja Digital previsto nas User Stories próprias da Sprint 2.

Assim, ainda existe valor funcional claro para a segunda entrega:

- identificação de colaborador DM;
- aprovação automática de Cartão DM para colaborador;
- reprovação automática de Cartão Loja para colaborador;
- regras específicas e comunicação do Cartão Loja Digital;
- evolução do processo de pré-qualificação.

### Sprint 3

Não foi criado painel administrativo para cadastrar lojistas, nem ofertas alternativas para clientes reprovados e nem atribuição de PACs a contribuidores.

Esses itens continuam disponíveis como valor principal da terceira entrega.

## Validações realizadas

Foram executadas validações locais com banco SQLite temporário para verificar a lógica da API sem depender do MySQL durante a revisão.

Validado:

- importação e compilação dos arquivos Python;
- sintaxe de todos os arquivos JavaScript;
- `GET /health`;
- listagem dos três cartões;
- busca de lojas usando CEP de SP;
- criação de solicitação de Cartão Loja Física;
- criação de solicitação de Cartão DM;
- retorno do status `EM_ANALISE`;
- consulta de uma solicitação criada.

O ambiente usado para revisar o ZIP não possui Docker instalado, portanto a execução completa do `docker compose up --build` não pôde ser feita aqui. O Compose foi ajustado para ficar consistente com os Dockerfiles do repositório.
