# API 2° Semestre ADS

# Documentação - Sprint 2

| Rank  | Prioridade |                                                        User Story                                                            | Estimativa de esforço | Sprint
|:-----:|:----------:|:----------------------------------------------------------------------------------------------------------------------------:|:----------:|:-----------:
|**1**|**Alta**|**Como sistema, quero verificar se o cliente é um colaborador DM, para aplicar a aprovação automática do Cartão DM**|**5**|**Sprint 2**|
|2|Alta|Como sistema, quero reprovar automaticamente pedidos de Cartão Loja feitos por colaboradores, para seguir a regra de negócio.|3|Sprint 2|
|4|Média|Como cliente, quero ser avisado que o Cartão Loja Digital não emite via física, para decidir com clareza antes de solicitar.|2|Sprint 2|
|5|Média|Como cliente, quero acompanhar o status do andamento da minha solicitação |3|Sprint 2|

## Valor entregue

A sprint 2 traz um novo design para a landing page e novas funcionalidades. O sistema teve seu design de front-end refeito, verifica de forma segura e automática a aprovabilidade de solicitações para colaboradores da DM, informa de forma clara o cliente de que o Cartão Loja Digital não é emitido em via física e permite o acompanhamento do status de andamento da solicitação do cartão.

## Critérios de aceitação atendidos
- Front-end inspirado nos sites próprios da empresa parceira (DM);
- O sistema verifica — de forma segura, sem evidenciar regras de aceitação para o público geral — se o CPF informado pertence a algum colaborador da empresa parceira (DM);
- A solicitação de um cartão DM sempre é aprovada para um colaborador;
- A solicitação de qualquer cartão que não seja o DM é reprovada para um colaborador;
- O sistema informa duplamente — na primeira e segunda etapa do campo de solicitação — o cliente sobre a não emissão de via física para o Cartão de Loja Digital;
- O campo de acompanhamento do status da solicitação permite ao cliente verificar o andamento de sua solicitação a partir de seu número de protocolo e CPF.

## Fluxo de demonstração

Para demonstrar a aprovação automática do Cartão DM, use um destes colaboradores fictícios cadastrados no banco de dados:

| CPF de demonstração | Perfil | Modalidade autorizada |
|---|---|---|
| 32376226643 | Colaborador Fictício 01 | Cartão DM |
| 33143237945 | Colaborador Fictício 02 | Cartão DM |
| 21953320694 | Colaborador Fictício 03 | Cartão DM |
| 63380575747 | Colaborador Fictício 04 | Cartão DM |

Os registros são criados automaticamente no início da API, sem duplicação e sem substituir cadastros existentes. São usados apenas para a demonstração acadêmica; a aprovação é uma pré-qualificação fictícia, não uma análise de crédito real.

Com um desses CPFs, uma solicitação de Cartão DM fica **APROVADA**. Solicitações de Cartão Loja Física ou Cartão Loja Digital ficam **REPROVADAS**. Clientes fora do cadastro de colaboradores permanecem **EM_ANALISE**, conforme a regra da sprint.

O formulário exige nome, CPF, e-mail, telefone e CEP válidos no formato esperado. Para Cartão Loja Física, a loja deve ser ativa e pertencer ao estado do CEP informado.

1. Solicitar Cartão DM utilizando um CPF cadastrado como colaborador DM.
2. Solicitar Cartão Loja Física utilizando o mesmo CPF e demonstrar a reprovação automática.
3. Realizar uma solicitação com CPF não cadastrado como colaborador e demonstrar o status "Em análise".
4. Consultar uma solicitação pelo protocolo e CPF, verificando o status retornado.
5. Mostrar os avisos sobre a ausência de emissão física do Cartão Loja Digital.

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

## Vídeo de Execução
<ul>
  <li>
    <a href=''>Video do funcionamento🎥 (Ainda não foi adicionado)</a>
  </li>  
</ul>
