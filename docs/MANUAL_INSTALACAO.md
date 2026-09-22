# Manual de Instalação

## Requisitos

- Git
- Docker
- Docker Compose

## Instalação

Clone o repositório e entre na pasta do projeto.

```bash
git clone URL_DO_REPOSITORIO
cd Projeto-API-2--Semestre-main
```

Suba os três serviços:

```bash
docker compose up --build
```

Aguarde o MySQL ficar saudável e o backend iniciar.

## Acessos

- Aplicação: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Variáveis de ambiente

O projeto possui valores padrão para desenvolvimento local. Caso queira alterar os dados do MySQL, copie `.env.example` para `.env` e edite os valores.

```bash
cp .env.example .env
```

## Encerrar

```bash
docker compose down
```

Para remover também os dados armazenados no volume do MySQL:

```bash
docker compose down -v
```
