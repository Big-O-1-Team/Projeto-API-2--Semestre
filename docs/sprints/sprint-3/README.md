# API 2° Semestre ADS

# Documentação - Sprint 3

| Rank | Prioridade | User Story | Estimativa de esforço | Sprint |
|:---:|:---:|:---|:---:|:---:|
| 9 | Média | Como administrador DM, quero cadastrar um novo lojista parceiro, para que clientes já consigam fazer PAC para ele. | 5 | Sprint 3 |
| 10 | Baixa | Como cliente reprovado, quero receber uma oferta de outro produto (EP, DMCred), para ter uma alternativa mesmo sem aprovação do cartão. | 5 | Sprint 3 |
| 11 | Baixa | Como parceiro, quero um campo para cadastrar nossos contribuidores, para atribuição das PACs a eles. | 5 | Sprint 3 |

## Valor entregue

A Sprint 3 amplia as funcionalidades do sistema, trazendo recursos para gerenciamento de lojas parceiras, cadastro de contribuidores e apresentação de ofertas alternativas para clientes que tiveram suas solicitações de cartão reprovadas.

Foi desenvolvida uma área administrativa para cadastro de novos lojistas parceiros e criação de seus respectivos acessos. Também foi implementada uma área para os parceiros gerenciarem seus contribuidores, permitindo que eles sejam associados às solicitações de PAC. A seleção do contribuidor durante a solicitação é opcional.

Além disso, o sistema passou a apresentar alternativas de produtos, como EP e DMCred, para clientes com solicitações reprovadas. O cliente pode manifestar interesse em uma oferta e autorizar o contato, sendo necessária a confirmação por meio de um link enviado por e-mail.

## Critérios de aceitação atendidos

- O administrador consegue cadastrar novos lojistas parceiros por meio de uma área administrativa.
- O cadastro de lojas possui validação de informações, incluindo UF e CEP.
- O sistema impede cadastros duplicados e protege as operações administrativas por autenticação via token.
- Os parceiros possuem acesso próprio ao sistema.
- O parceiro consegue cadastrar e gerenciar seus contribuidores.
- Os contribuidores são vinculados às respectivas lojas.
- O preenchimento do contribuidor durante uma solicitação é opcional.
- O sistema permite buscar lojas por nome e cidade.
- Solicitações reprovadas apresentam alternativas de produtos, incluindo EP e DMCred.
- O cliente pode manifestar interesse em uma das ofertas apresentadas.
- O sistema solicita autorização do cliente para receber contato.
- A confirmação do consentimento acontece por meio de um link enviado ao e-mail do cliente.
- O sistema não considera o consentimento confirmado antes da interação do cliente com o link recebido.
- O envio de e-mails utiliza serviço SMTP configurável por variáveis de ambiente.

## Fluxo de demonstração

### Cadastro de lojas parceiras e contribuidores

1. Acessar a área administrativa de parceiros.
2. Realizar o cadastro de um novo lojista, preenchendo as informações solicitadas.
3. Demonstrar as validações de UF e CEP e a proteção contra cadastros duplicados.
4. Criar ou demonstrar o acesso do parceiro.
5. Acessar a área do parceiro utilizando suas credenciais.
6. Cadastrar novos contribuidores vinculados à loja.
7. Demonstrar a listagem e a busca de lojas por nome ou cidade.
8. Iniciar uma solicitação e demonstrar que a seleção de um contribuidor é opcional.

### Ofertas alternativas e confirmação de consentimento

1. Realizar uma solicitação de cartão em um cenário que resulte em reprovação.
2. Demonstrar a apresentação das ofertas alternativas EP e DMCred.
3. Selecionar uma das ofertas e manifestar interesse.
4. Demonstrar a solicitação de consentimento para contato.
5. Confirmar o envio do e-mail com o link de autorização.
6. Acessar o link recebido e demonstrar a confirmação do consentimento.

## DoR - Definition of Ready

| Critério | Descrição |
|:---:|---|
| Clareza na Descrição | A User Story está escrita no formato “Como [persona], quero [ação] para que [objetivo]”. |
| Critérios de Aceitação Definidos | A história possui critérios objetivos que indicam o que é necessário para considerá-la concluída. |
| Independente | A história pode ser implementada sem depender de outra tarefa da mesma Sprint. |
| Compreensão Compartilhada | Toda a equipe, incluindo PO e desenvolvedores, compreende o propósito da história. |

## DoD - Definition of Done

| Critério | Descrição |
|:---:|---|
| Critérios de Aceitação atendidos | Os cenários previstos para cada User Story foram implementados. |
| Código revisado | O código deve ser revisado pela equipe. |
| Testes realizados | Os testes automatizados de backend e as verificações de frontend foram executados. |
| Validação do PO | O Product Owner valida a entrega com base nos critérios definidos. |
| Pronto para entrega | O item está funcional e pode ser demonstrado ao parceiro/professor. |
| Documentação atualizada | A documentação da Sprint foi atualizada no repositório. |

## Vídeo de Execução

Adicionar o link do vídeo de demonstração da Sprint 3 após sua publicação.
