# Backend - Python (FastAPI)

API REST para o Projeto Cidadão.

## Instalação

```bash
cd backend
pip install -r requirements.txt
```

## Executar

```bash
uvicorn main:app --reload
```

## Endpoints

- `GET /api/executivo/transparencia` - Dados do Portal da Transparência
- `GET /api/legislativo/proposicoes` - Proposições legislativas
- `GET /api/judiciario/processos` - Processos judiciais