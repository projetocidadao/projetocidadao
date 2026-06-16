"""schema inicial: usuarios, areas, cursos, modulos, progressos, denuncias, anexos, comentarios, casos_suspeitos, heuristicas

Revision ID: 001
Revises:
Create Date: 2026-06-16 00:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === Enums ===
    role_enum = postgresql.ENUM(
        "cidadao", "avancado", "pioneiro", "moderador", "admin",
        name="role_enum", create_type=True,
    )
    status_curso_enum = postgresql.ENUM(
        "incubacao", "em_aprovacao", "publicado", "rejeitado", "arquivado",
        name="status_curso_enum", create_type=True,
    )
    status_denuncia_enum = postgresql.ENUM(
        "aguardando", "em_analise", "em_andamento", "resolvida", "rejeitada", "arquivada",
        name="status_denuncia_enum", create_type=True,
    )
    canal_denuncia_enum = postgresql.ENUM(
        "cgu", "ministerio_publico", "tcu", "tce",
        "ouvidoria_federal", "ouvidoria_estadual", "ouvidoria_municipal",
        "defensoria", "ibama", "policia_federal", "outro",
        name="canal_denuncia_enum", create_type=True,
    )
    tipo_alvo_enum = postgresql.ENUM(
        "denuncia", "curso", "area", "caso_suspeito",
        name="tipo_alvo_enum", create_type=True,
    )
    status_caso_enum = postgresql.ENUM(
        "novo", "em_analise", "investigado", "confirmado", "falso_positivo", "arquivado",
        name="status_caso_enum", create_type=True,
    )
    tipo_caso_enum = postgresql.ENUM(
        "licitacao", "contrato", "folha", "transferencia", "cruzamento", "empresa", "pessoa",
        name="tipo_caso_enum", create_type=True,
    )

    role_enum.create(op.get_bind(), checkfirst=True)
    status_curso_enum.create(op.get_bind(), checkfirst=True)
    status_denuncia_enum.create(op.get_bind(), checkfirst=True)
    canal_denuncia_enum.create(op.get_bind(), checkfirst=True)
    tipo_alvo_enum.create(op.get_bind(), checkfirst=True)
    status_caso_enum.create(op.get_bind(), checkfirst=True)
    tipo_caso_enum.create(op.get_bind(), checkfirst=True)

    # === Tabela: usuarios ===
    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("biografia", sa.String(500)),
        sa.Column("cidade", sa.String(100)),
        sa.Column("estado", sa.String(2)),
        sa.Column("pontos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("role", role_enum, nullable=False, server_default="cidadao"),
        sa.Column("data_primeira_contribuicao", sa.DateTime(timezone=True)),
        sa.Column("apto_a_criar", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("consentimento_lgpd", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("data_consentimento", sa.DateTime(timezone=True)),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)
    op.create_index("ix_usuarios_pontos", "usuarios", ["pontos"])

    # === Tabela: areas ===
    op.create_table(
        "areas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("icone", sa.String(50), nullable=False),
        sa.Column("cor", sa.String(7), nullable=False, server_default="#000000"),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_areas_slug", "areas", ["slug"], unique=True)

    # === Tabela: cursos ===
    op.create_table(
        "cursos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("titulo", sa.String(300), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("status", status_curso_enum, nullable=False, server_default="incubacao"),
        sa.Column("autor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("area_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("areas.id"), nullable=False),
        sa.Column("visualizacoes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("concluidos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duracao_minutos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_cursos_slug", "cursos", ["slug"], unique=True)
    op.create_index("ix_cursos_status", "cursos", ["status"])

    # === Tabela: modulos ===
    op.create_table(
        "modulos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("curso_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("titulo", sa.String(300), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duracao_minutos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # === Tabela: progressos ===
    op.create_table(
        "progressos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("curso_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("concluido", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("usuario_id", "curso_id", name="uq_progresso_usuario_curso"),
    )

    # === Tabela: denuncias ===
    op.create_table(
        "denuncias",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("titulo", sa.String(300), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("categoria", sa.String(100), nullable=False),
        sa.Column("area_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("areas.id"), nullable=False),
        sa.Column("status", status_denuncia_enum, nullable=False, server_default="aguardando"),
        sa.Column("canal_destino", canal_denuncia_enum),
        sa.Column("codigo_rastreio", sa.String(20), nullable=False),
        sa.Column("anonima", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("autor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id")),
        sa.Column("lat", sa.Float()),
        sa.Column("lng", sa.Float()),
        sa.Column("endereco", sa.String(500)),
        sa.Column("municipio", sa.String(100)),
        sa.Column("estado", sa.String(2)),
        sa.Column("data_fato", sa.DateTime(timezone=True)),
        sa.Column("valor_dano_estimado", sa.Float()),
        sa.Column("votos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visualizacoes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("resposta_oficial", sa.Text()),
        sa.Column("data_resposta", sa.DateTime(timezone=True)),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_denuncias_codigo_rastreio", "denuncias", ["codigo_rastreio"], unique=True)
    op.create_index("ix_denuncias_categoria", "denuncias", ["categoria"])
    op.create_index("ix_denuncias_area_id", "denuncias", ["area_id"])
    op.create_index("ix_denuncias_status", "denuncias", ["status"])
    op.create_index("ix_denuncias_autor_id", "denuncias", ["autor_id"])
    op.create_index("ix_denuncias_municipio", "denuncias", ["municipio"])
    op.create_index("ix_denuncias_estado", "denuncias", ["estado"])
    op.create_index("ix_denuncias_canal_destino", "denuncias", ["canal_destino"])
    op.create_index("ix_denuncias_criado_em", "denuncias", ["criado_em"])

    # === Tabela: anexos ===
    op.create_table(
        "anexos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("denuncia_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("denuncias.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("tamanho_bytes", sa.Integer(), nullable=False),
        sa.Column("hash_sha256", sa.String(64)),
        sa.Column("descricao", sa.String(300)),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # === Tabela: comentarios ===
    op.create_table(
        "comentarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("autor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("tipo_alvo", tipo_alvo_enum, nullable=False),
        sa.Column("alvo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("comentarios.id")),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_comentarios_tipo_alvo", "comentarios", ["tipo_alvo"])
    op.create_index("ix_comentarios_alvo_id", "comentarios", ["alvo_id"])

    # === Tabela: casos_suspeitos ===
    op.create_table(
        "casos_suspeitos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tipo", tipo_caso_enum, nullable=False),
        sa.Column("referencia_id", sa.String(200)),
        sa.Column("titulo", sa.String(500), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("score_risco", sa.Float(), nullable=False, server_default="0"),
        sa.Column("severidade", sa.String(20), nullable=False, server_default="BAIXA"),
        sa.Column("dados", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", status_caso_enum, nullable=False, server_default="novo"),
        sa.Column("denuncia_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("denuncias.id")),
        sa.Column("detectado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_casos_suspeitos_tipo", "casos_suspeitos", ["tipo"])
    op.create_index("ix_casos_suspeitos_referencia_id", "casos_suspeitos", ["referencia_id"])
    op.create_index("ix_casos_suspeitos_score_risco", "casos_suspeitos", ["score_risco"])
    op.create_index("ix_casos_suspeitos_severidade", "casos_suspeitos", ["severidade"])
    op.create_index("ix_casos_suspeitos_status", "casos_suspeitos", ["status"])

    # === Tabela: heuristicas ===
    op.create_table(
        "heuristicas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("caso_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("casos_suspeitos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("codigo", sa.String(10), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("peso", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("evidencia", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("detectado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )


def downgrade() -> None:
    op.drop_table("heuristicas")
    op.drop_table("casos_suspeitos")
    op.drop_table("comentarios")
    op.drop_table("anexos")
    op.drop_table("denuncias")
    op.drop_table("progressos")
    op.drop_table("modulos")
    op.drop_table("cursos")
    op.drop_table("areas")
    op.drop_table("usuarios")

    op.execute("DROP TYPE IF EXISTS tipo_caso_enum")
    op.execute("DROP TYPE IF EXISTS status_caso_enum")
    op.execute("DROP TYPE IF EXISTS tipo_alvo_enum")
    op.execute("DROP TYPE IF EXISTS canal_denuncia_enum")
    op.execute("DROP TYPE IF EXISTS status_denuncia_enum")
    op.execute("DROP TYPE IF EXISTS status_curso_enum")
    op.execute("DROP TYPE IF EXISTS role_enum")
