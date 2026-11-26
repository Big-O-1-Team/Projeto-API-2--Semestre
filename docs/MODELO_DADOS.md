# Modelo relacional

```mermaid
erDiagram
    REDES_PARCEIRAS ||--o{ PROGRAMAS_CARTAO : possui
    PROGRAMAS_CARTAO ||--o{ PROGRAMA_UNIDADES : vincula
    ESTABELECIMENTOS_PARCEIROS ||--o{ PROGRAMA_UNIDADES : participa
    USUARIOS ||--o{ SOLICITACOES : realiza
    PROGRAMAS_CARTAO o|--o{ SOLICITACOES : identifica
    ESTABELECIMENTOS_PARCEIROS o|--o{ SOLICITACOES : origina
    ESTABELECIMENTOS_PARCEIROS ||--o| CONTAS_PARCEIROS : administra
    ESTABELECIMENTOS_PARCEIROS ||--o{ CONTRIBUIDORES_PARCEIROS : possui
    CONTRIBUIDORES_PARCEIROS o|--o{ SOLICITACOES : atende
    SOLICITACOES ||--o| INTERESSES_OFERTAS : gera
```

Usuários: CPF e e-mail únicos. Solicitações: usuário, modalidade, unidade, programa, atendente, status e data. A chave ativa única evita duplicação entre unidades do mesmo programa. O hash do código privado protege a consulta; a localização do cliente não é persistida pelo aplicativo. Colaboradores DM e catálogo de cartões são tabelas independentes. Modelos completos em backend/app/models.

Uma unidade pode participar de vários programas. A chave composta (loja_id, programa_id) impede vínculos repetidos. A DM deve confirmar a abrangência contratual de cada programa antes de cadastrar unidades reais.
