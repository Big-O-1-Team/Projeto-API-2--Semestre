# API 2° Semestre ADS

# Documentação - Sprint 1

| Rank | Prioridade | User Story | Estimativa de esforço | Sprint |
|:---:|:---:|:---|:---:|:---:|
| 1 | Alta | Como cliente, quero preencher meus dados pessoais, para iniciar minha solicitação de cartão. | 3 | Sprint 1 |
| 2 | Alta | Como cliente, quero escolher entre Cartão DM e Cartão Loja (física ou digital), para solicitar o produto que desejo. | 1 | Sprint 1 |
| 3 | Média | Como cliente não colaborador, quero que minha solicitação seja marcada como "em análise" quando não for aprovada de imediato, para saber o status do meu pedido. | 5 | Sprint 1 |
| 4 | Média | Como cliente, quero informar meu CEP ao pedir Cartão Loja física, para que o sistema me mostre só lojas do meu estado. | 5 | Sprint 1 |

## Valor entregue

A Sprint 1 possui um fluxo funcional de ponta a ponta. O usuário escolhe o cartão, informa seus dados, consulta lojas parceiras pelo CEP quando necessário, envia a solicitação e recebe o status inicial `EM_ANALISE` com um número de protocolo.

## Critérios de aceitação atendidos

- formulário coleta nome, CPF, e-mail, telefone e CEP;
- dados são persistidos no banco;
- usuário pode selecionar o tipo de cartão;
- Cartão Loja Física exige uma loja parceira;
- busca por CEP retorna somente lojas do estado identificado;
- backend impede seleção de uma loja de outro estado;
- solicitação gera protocolo próprio;
- status inicial da Sprint 1 é `EM_ANALISE`;
- interface funciona em desktop e celular;
- API possui documentação Swagger em `/docs`.

## Fluxo de demonstração

Use `12210-000` para demonstrar a busca de lojas em SP.

1. Escolher Cartão Loja Física.
2. Informar os dados pessoais.
3. Buscar as lojas pelo CEP.
4. Selecionar uma loja.
5. Enviar.
6. Conferir o protocolo e o status Em análise.

## DoR - Definition of Ready

| Critério | Descrição |
|:---:|---|
| Clareza na Descrição | A User Story está escrita no formato “Como [persona], quero [ação] para que [objetivo]”. |
| Critérios de Aceitação Definidos | A história possui critérios objetivos que indicam o que é necessário para considerá-la concluída. |
| Independente | A história pode ser implementada sem depender de outra tarefa da mesma Sprint. |
| Compreensão Compartilhada | Toda a equipe, incluindo PO e devs, compreende o propósito da história. |

## DoD - Definition of Done

| Critério | Descrição |
|:---:|---|
| Critérios de Aceitação atendidos | Todos os cenários previstos para a história foram implementados. |
| Código revisado | O código deve ser revisado pela equipe antes do fechamento. |
| Validação do PO | O Product Owner valida a entrega com base nos critérios definidos. |
| Pronto para entrega | O item está funcional e pode ser demonstrado ao parceiro/professor. |

## Próximas Sprints

As regras de identificação de colaboradores, aprovação/reprovação automática e evolução do Cartão Loja Digital continuam para a Sprint 2. O painel de cadastro de parceiros, ofertas alternativas e atribuição de PACs continuam para a Sprint 3.
