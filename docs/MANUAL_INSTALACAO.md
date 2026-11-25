# Instalação

Requisitos: Git, Docker e Docker Compose.

```bash
git clone https://github.com/Big-O-1-Team/Projeto-API-2--Semestre.git
cd Projeto-API-2--Semestre
git switch feat/integracao-dm-redes-localizacao
cp .env.example .env
docker compose up --build
```

Antes de iniciar, configure AUTH_SECRET e ADMIN_TOKEN com valores aleatórios de pelo menos 32 caracteres. Não publique o .env. Se a porta 3306 estiver ocupada, remova o mapeamento de porta do serviço mysql (o backend usa a rede interna).

Aplicação: http://localhost:5173  
API: http://localhost:8000/docs  
Admin: http://localhost:5173/admin-parceiros.html  
Parceiro: http://localhost:5173/parceiro.html

Para testar aprovação fictícia de não colaboradores, configure DEMO_PRE_QUALIFICACAO=1 e PRE_QUALIFICADOS_FICTICIOS como JSON com CPF de teste e lista de modalidades. Por padrão essa aprovação está desativada. Não use dados reais.

SMTP exige SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM e PUBLIC_API_URL acessível. Sem SMTP, o sistema não afirma que enviou e-mail. Localização exige HTTPS ou localhost e consentimento do navegador. O ViaCEP precisa estar acessível para validar o CEP informado. Nos testes automatizados, CEP_API_BASE_URL aponta para um serviço simulado.

```bash
docker compose down
```

Não use down -v em banco com dados a preservar. Faça backup antes da migração de uma instalação existente. Solicitações legadas não têm código privado. Após verificar a identidade do titular por canal seguro, um administrador pode gerar um novo código em POST /solicitacoes/{id}/codigo (invalida o anterior).
