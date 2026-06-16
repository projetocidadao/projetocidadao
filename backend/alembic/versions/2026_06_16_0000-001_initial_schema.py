"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============== ENUMS ==============
    user_role = postgresql.ENUM(
        "cidadao", "avancado", "moderador", "admin",
        name="user_role", create_type=True,
    )
    status_denuncia = postgresql.ENUM(
        "aguardando", "em_analise", "em_andamento", "resolvida", "rejeitada",
        name="status_denuncia", create_type=True,
    )
    categoria_denuncia = postgresql.ENUM(
        "saude", "educacao", "alimentacao", "transporte", "seguranca",
        "saneamento", "financas", "meio_ambiente", "cultura", "outro",
        name="categoria_denuncia", create_type=True,
    )
    tipo_anexo = postgresql.ENUM(
        "foto", "video", "pdf", "audio", "outro",
        name="tipo_anexo", create_type=True,
    )
    tipo_notificacao = postgresql.ENUM(
        "denuncia_criada", "denuncia_atualizada", "comentario_novo",
        "curso_concluido", "farejador_alerta", "sistema",
        name="tipo_notificacao", create_type=True,
    )
    status_faro = postgresql.ENUM(
        "novo", "em_analise", "investigado", "arquivado", "confirmado",
        name="status_faro", create_type=True,
    )

    # ============== USUARIOS ==============
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="cidadao"),
        sa.Column("pontos", sa.Integer, nullable=False, server_default="0"),
        sa.Column("nivel", sa.Integer, nullable=False, server_default="1"),
        sa.Column("bio", sa.String(500), nullable=True),
        sa.Column("cidade", sa.String(100), nullable=True),
        sa.Column("estado", sa.String(2), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("verificado", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("ultimo_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ============== AREAS ==============
    op.create_table(
        "areas",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("slug", sa.String(80), unique=True, index=True, nullable=False),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("descricao", sa.String(1000), nullable=False),
        sa.Column("icone", sa.String(50), nullable=False),
        sa.Column("cor", sa.String(7), nullable=True),
        sa.Column("artigo_cf", sa.String(50), nullable=True),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ============== CURSOS ==============
    op.create_table(
        "cursos",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("slug", sa.String(120), unique=True, index=True, nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descricao", sa.String(1000), nullable=False),
        sa.Column("conteudo", sa.Text, nullable=False),
        sa.Column("duracao_minutos", sa.Integer, nullable=False, server_default="60"),
        sa.Column("nivel", sa.String(20), nullable=False, server_default="iniciante"),
        sa.Column("publico_alvo", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="publicado"),
        sa.Column("autor_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("total_modulos", sa.Integer, nullable=False, server_default="1"),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("area_id", sa.Integer, sa.ForeignKey("areas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ============== DENUNCIAS ==============
    op.create_table(
        "denuncias",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=False),
        sa.Column("categoria", categoria_denuncia, nullable=False, index=True),
        sa.Column("status", status_denuncia, nullable=False, server_default="aguardando", index=True),
        sa.Column("anonima", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("publica", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("lat", sa.Float, nullable=True),
        sa.Column("lng", sa.Float, nullable=True),
        sa.Column("endereco", sa.String(500), nullable=True),
        sa.Column("municipio", sa.String(100), nullable=True, index=True),
        sa.Column("estado", sa.String(2), nullable=True, index=True),
        sa.Column("cep", sa.String(10), nullable=True, index=True),
        sa.Column("data_fato", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valor_dano_estimado", sa.Float, nullable=True),
        sa.Column("envolvidos", sa.Text, nullable=True),
        sa.Column("canal_destino", sa.String(100), nullable=True),
        sa.Column("codigo_rastreio", sa.String(20), unique=True, index=True, nullable=False),
        sa.Column("votos", sa.Integer, nullable=False, server_default="0"),
        sa.Column("visualizacoes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("autor_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("area_id", sa.Integer, sa.ForeignKey("areas.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ============== ANEXOS ==============
    op.create_table(
        "anexos",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("nome_original", sa.String(255), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("tamanho_bytes", sa.BigInteger, nullable=True),
        sa.Column("tipo", tipo_anexo, nullable=False),
        sa.Column("hash_sha256", sa.String(64), nullable=True, index=True),
        sa.Column("denuncia_id", sa.Integer, sa.ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ============== COMENTARIOS ==============
    op.create_table(
        "comentarios",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("texto", sa.Text, nullable=False),
        sa.Column("editado", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("comentarios.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("autor_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("denuncia_id", sa.Integer, sa.ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ============== PROGRESSOS ==============
    op.create_table(
        "progressos",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("curso_id", sa.Integer, sa.ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("percentual", sa.Integer, nullable=False, server_default="0"),
        sa.Column("concluido", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("data_conclusao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pontos_ganhos", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("usuario_id", "curso_id", name="uq_progresso_usuario_curso"),
    )

    # ============== VOTOS ==============
    op.create_table(
        "votos",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("denuncia_id", sa.Integer, sa.ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False),
        sa.Column("apoio", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("pontos", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("usuario_id", "denuncia_id", name="uq_voto_usuario_denuncia"),
    )

    # ============== FAROS (Farejador) ==============
    op.create_table(
        "faros",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("tipo_entidade", sa.String(30), nullable=False, index=True),
        sa.Column("referencia_id", sa.String(100), nullable=False, index=True),
        sa.Column("entidade_nome", sa.String(255), nullable=True),
        sa.Column("heuristicas", sa.JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("evidencia", sa.JSON, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("score_risco", sa.Integer, nullable=False, server_default="0", index=True),
        sa.Column("severidade", sa.String(20), nullable=False, server_default="MEDIA", index=True),
        sa.Column("status", status_faro, nullable=False, server_default="novo", index=True),
        sa.Column("data_deteccao", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("data_investigacao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("desfecho", sa.Text, nullable=True),
        sa.Column("denuncia_id", sa.Integer, sa.ForeignKey("denuncias.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ============== NOTIFICACOES ==============
    op.create_table(
        "notificacoes",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("mensagem", sa.Text, nullable=False),
        sa.Column("tipo", tipo_notificacao, nullable=False),
        sa.Column("lida", sa.Boolean, nullable=False, server_default=sa.false(), index=True),
        sa.Column("data_leitura", sa.DateTime(timezone=True), nullable=True),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ============== POSTGRES EXTENSIONS ==============
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")  # para dados geográficos
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")  # para busca textual


def downgrade() -> None:
    op.drop_table("notificacoes")
    op.drop_table("faros")
    op.drop_table("votos")
    op.drop_table("progressos")
    op.drop_table("comentarios")
    op.drop_table("anexos")
    op.drop_table("denuncias")
    op.drop_table("cursos")
    op.drop_table("areas")
    op.drop_table("usuarios")
    op.execute("DROP TYPE IF EXISTS status_faro")
    op.execute("DROP TYPE IF EXISTS tipo_notificacao")
    op.execute("DROP TYPE IF EXISTS tipo_anexo")
    op.execute("DROP TYPE IF EXISTS categoria_denuncia")
    op.execute("DROP TYPE IF EXISTS status_denuncia")
    op.execute("DROP TYPE IF EXISTS user_role")
