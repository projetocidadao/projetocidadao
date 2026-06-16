"""
Templates de mensagens — renderização por tipo de notificação.
Suporta formatação HTML para Telegram e texto puro para in-app/email.
"""
from typing import Dict, Any
from src.models.enums import TipoNotificacao, SeveridadeFaro


def renderizar_mensagem(
    tipo: TipoNotificacao,
    dados: Dict[str, Any],
    canal: str = "in_app",
) -> Dict[str, str]:
    """
    Renderiza título e mensagem para uma notificação.
    Retorna dict com `titulo` e `mensagem` (HTML para Telegram, texto para in-app).
    """
    if tipo == TipoNotificacao.FARO_CRITICO:
        return _tpl_faro_critico(dados, canal)
    if tipo == TipoNotificacao.FARO_NOVO:
        return _tpl_faro_novo(dados, canal)
    if tipo == TipoNotificacao.NOVA_DENUNCIA:
        return _tpl_nova_denuncia(dados, canal)
    if tipo == TipoNotificacao.DENUNCIA_STATUS:
        return _tpl_denuncia_status(dados, canal)
    if tipo == TipoNotificacao.COMENTARIO_RESPOSTA:
        return _tpl_comentario_resposta(dados, canal)
    if tipo == TipoNotificacao.VOTO_RECEBIDO:
        return _tpl_voto_recebido(dados, canal)
    if tipo == TipoNotificacao.NIVEL_UP:
        return _tpl_nivel_up(dados, canal)
    if tipo == TipoNotificacao.CURSO_CONCLUIDO:
        return _tpl_curso_concluido(dados, canal)
    return _tpl_sistema(dados, canal)


def _tpl_faro_critico(dados: dict, canal: str) -> dict:
    severidade = dados.get("severidade", "ALTA")
    score = dados.get("score_risco", 0)
    titulo_denuncia = dados.get("titulo", "Denúncia")
    codigo = dados.get("codigo_rastreio", "PC-XXXX")
    heuristicas = dados.get("heuristicas", [])

    emoji = "🚨" if severidade == "CRITICA" else "⚠️"

    titulo = f"{emoji} Faro {severidade} detectado (score {score})"

    if canal == "telegram":
        lista_heuristicas = "\n".join(f"  • <code>{h}</code>" for h in heuristicas[:5])
        mensagem = (
            f"<b>{emoji} ALERTA DE CORRUPÇÃO</b>\n\n"
            f"<b>{titulo_denuncia}</b>\n"
            f"Código: <code>{codigo}</code>\n"
            f"Score: <b>{score}/100</b> · Severidade: <b>{severidade}</b>\n\n"
            f"<b>Sinais detectados:</b>\n{lista_heuristicas}\n\n"
            f"🔍 <a href=\"https://projetocidadao.org/faros/{dados.get('faro_id')}\">"
            f"Ver detalhes</a>"
        )
    else:
        lista_heuristicas = ", ".join(heuristicas[:5])
        mensagem = (
            f"Alerta de corrupção detectado na denúncia '{titulo_denuncia}' "
            f"(código {codigo}). Score {score}/100 — Severidade {severidade}. "
            f"Sinais: {lista_heuristicas}."
        )
    return {"titulo": titulo, "mensagem": mensagem}


def _tpl_faro_novo(dados: dict, canal: str) -> dict:
    return _tpl_faro_critico(dados, canal)  # mesmo template


def _tpl_nova_denuncia(dados: dict, canal: str) -> dict:
    titulo_denuncia = dados.get("titulo", "Nova denúncia")
    categoria = dados.get("categoria", "")
    municipio = dados.get("municipio", "")
    estado = dados.get("estado", "")
    local = f"{municipio}/{estado}" if municipio else "Brasil"

    titulo = f"📢 Nova denúncia em {local}"
    if canal == "telegram":
        mensagem = (
            f"<b>📢 Nova denúncia em {local}</b>\n\n"
            f"<b>{titulo_denuncia}</b>\n"
            f"Categoria: {categoria}\n"
            f"🔗 <a href=\"https://projetocidadao.org/denuncias/{dados.get('denuncia_id')}\">"
            f"Ver denúncia</a>"
        )
    else:
        mensagem = f"Nova denúncia em {local}: {titulo_denuncia} (categoria: {categoria})."
    return {"titulo": titulo, "mensagem": mensagem}


def _tpl_denuncia_status(dados: dict, canal: str) -> dict:
    status_anterior = dados.get("status_anterior", "")
    novo_status = dados.get("novo_status", "")
    titulo_denuncia = dados.get("titulo", "sua denúncia")

    titulo = f"🔄 Denúncia atualizada: {novo_status}"
    if canal == "telegram":
        mensagem = (
            f"<b>🔄 Status atualizado</b>\n\n"
            f"Sua denúncia <b>{titulo_denuncia}</b> mudou de "
            f"<code>{status_anterior}</code> para <code>{novo_status}</code>.\n\n"
            f"🔗 <a href=\"https://projetocidadao.org/denuncias/{dados.get('denuncia_id')}\">"
            f"Acompanhar</a>"
        )
    else:
        mensagem = f"Sua denúncia '{titulo_denuncia}' mudou de '{status_anterior}' para '{novo_status}'."
    return {"titulo": titulo, "mensagem": mensagem}


def _tpl_comentario_resposta(dados: dict, canal: str) -> dict:
    autor = dados.get("autor", "Alguém")
    trecho = dados.get("trecho", "")[:120]
    return {
        "titulo": f"💬 {autor} respondeu",
        "mensagem": f"{autor} comentou: \"{trecho}...\"" if canal == "in_app" else f"<b>💬 {autor}</b> respondeu:\n\n<i>{trecho}...</i>",
    }


def _tpl_voto_recebido(dados: dict, canal: str) -> dict:
    peso = dados.get("peso", 1)
    apoio = dados.get("apoio", True)
    emoji = "👍" if apoio else "👎"
    return {
        "titulo": f"{emoji} Seu voto foi registrado",
        "mensagem": f"Você {'apoiou' if apoio else 'contestou'} (peso {peso}) a denúncia {dados.get('codigo_rastreio', '')}.",
    }


def _tpl_nivel_up(dados: dict, canal: str) -> dict:
    nivel = dados.get("nivel", 2)
    pontos = dados.get("pontos", 0)
    return {
        "titulo": f"⭐ Você subiu para o nível {nivel}!",
        "mensagem": f"Parabéns! Você atingiu {pontos} pontos e subiu para o nível {nivel}.",
    }


def _tpl_curso_concluido(dados: dict, canal: str) -> dict:
    curso = dados.get("curso", "o curso")
    return {
        "titulo": f"🎓 Curso concluído: {curso}",
        "mensagem": f"Você concluiu {curso} e ganhou {dados.get('pontos', 50)} pontos!",
    }


def _tpl_sistema(dados: dict, canal: str) -> dict:
    return {
        "titulo": dados.get("titulo", "📢 Aviso do sistema"),
        "mensagem": dados.get("mensagem", ""),
    }
