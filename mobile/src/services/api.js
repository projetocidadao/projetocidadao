/**
 * API Service - Conexão com backend Python
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Executivo
export const getBolsaFamilia = (cpf, nis) => 
  api.get('/executivo/transparencia/bolsa-familia', { params: { cpf, nis } });

export const getConvenios = (cnpj, mes) => 
  api.get('/executivo/transparencia/convenios', { params: { cnpj_favorecido: cnpj, mes } });

export const getLicitacoes = (ua, modalidade, ano) => 
  api.get('/executivo/compras/licitacoes', { params: { ua, modalidae: modalidade, ano } });

export const getContratos = (idLicitacao, cnpj) => 
  api.get('/executivo/compras/contratos', { params: { id_licitacao: idLicitacao, cnpj } });

// Legislativo
export const getDeputados = (nome, estado) => 
  api.get('/legislativo/camara/deputados', { params: { nome, estado } });

export const getProposicoes = (ano, tipo, autor) => 
  api.get('/legislativo/camara/proposicoes', { params: { ano, tipo, autor } });

export const getVotacoes = (idProposicao) => 
  api.get(`/legislativo/camara/votacoes/${idProposicao}`);

export const getSenadores = (nome) => 
  api.get('/legislativo/senado/senadores', { params: { nome } });

// Judiciário
export const getTribunais = () => 
  api.get('/judiciario/cnj/tribunais');

export const getProcessos = (tribunal, ano, classe) => 
  api.get('/judiciario/cnj/processos', { params: { tribunal, ano, classe } });

export const getEstatisticas = (tribunal, periodo) => 
  api.get('/judiciario/cnj/estatisticas', { params: { tribunal, periodo } });

export default api;