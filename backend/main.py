\"""
Projeto Cidadão - Backend API
FastAPI para integração com fontes de dados públicos
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.integracoes import executivo, legislativo, judiciario

app = FastAPI(title="Projeto Cidadão API", description="API de transparência pública")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Executivo
app.include_router(executivo.router, prefix="/api/executivo", tags=["Executivo"])

# Legislativo
app.include_router(legislativo.router, prefix="/api/legislativo", tags=["Legislativo"])

# Judiciário
app.include_router(judiciario.router, prefix="/api/judiciario", tags=["Judiciário"])

@app.get("/")
def root():
    return {"message": "Projeto Cidadão API - Transparência Pública"}

@app.get("/health")
def health():
    return {"status": "ok"}