# 🎮 Sistema de Gamificação

Documento oficial do sistema de pontos, badges e níveis do Projeto Cidadão.

## 🎯 Filosofia

A gamificação do Projeto Cidadão tem 3 princípios:

1. **Transparência radical** — todas as regras são públicas e auditáveis
2. **Mérito distribuído** — quanto mais pioneiro, mais bonificado (com teto)
3. **Impacto real** — pontos viram permissões, não só números de vaidade

---

## 💰 Tabela de Pontos

| Ação | Pontos | Limite/dia |
|------|--------|-------------|
| Criar curso novo | +50 | 3/dia |
| Curso aprovado | +100 | — |
| Curso avaliado (5⭐) | +20 | 10/dia |
| Comentário útil | +5 | 20/dia |
| Denúncia validada | +30 | 5/dia |
| Fiscalização concluída | +200 | 2/dia |
| Moderar conteúdo | +15 | 10/dia |
| Streak diário (7 dias) | +50 | 1/semana |
| Indicar amigo aprovado | +75 | 3/dia |

---

## 🏆 Níveis e Permissões

Os pontos definem seu nível e **o que você pode fazer** na plataforma:

| Nível | Pontos | Permissões | Badge |
|-------|--------|------------|-------|
| 🥉 Aprendiz | 0–100 | Visualizar, comentar | 🌱 |
| 🥈 Cidadão | 101–500 | Criar cursos, denunciar | 🏛️ |
| 🥇 Guardião | 501–2.000 | Avaliar cursos, propor mudanças | ⚖️ |
| 💎 Magistrado | 2.001–5.000 | Moderar, editar qualquer curso | 👑 |
| 🏛️ Senador | 5.000+ | Todas + voto decisivo em governança | 🏛️ |

### Como subir de nível?
- Pontos são **acumulativos** (nunca decaem)
- Permissões são **conquistadas** ao atingir o nível
- Semanalmente, o sistema revisa se a atividade continua consistente

---

## 🎖️ Badges Temáticos (3 Poderes)

Badges especiais baseados nos **3 Poderes da República**:

### 👔 Poder Executivo
| Badge | Como conseguir | Recompensa |
|-------|----------------|------------|
| 🏛️ Fundador | Criar o primeiro curso da categoria | +200 pts |
| 📊 Analista | 10 cursos avaliados com nota ≥ 4⭐ | +100 pts |
| 💼 Gestor | 50 fiscalizações concluídas | +500 pts |

### ⚖️ Poder Judiciário
| Badge | Como conseguir | Recompensa |
|-------|----------------|------------|
| ⚖️ Árbitro | 100 mediações de conflitos | +300 pts |
| 📜 Jurista | Criar 5 cursos sobre legislação | +250 pts |
| 🏛️ Magistrado Real | Chegar ao nível Magistrado | Permanente |

### 📜 Poder Legislativo
| Badge | Como conseguir | Recompensa |
|-------|----------------|------------|
| 📜 Proponente | 25 proposals aceitas pela comunidade | +400 pts |
| 🗳️ Eleitor | Votar em 50 governanças | +150 pts |
| 🏛️ Senador Real | Chegar ao nível Senador | Permanente |

---

## 🛡️ Sistema Anti-Cheat

Pra evitar vícios e manipulação, o sistema tem:

| Fraude comum | Detecção | Penalidade |
|--------------|----------|------------|
| Criar cursos vazios/fake | Análise de texto (mín. 300 palavras + 3 anexos) | -100 pts + curso apagado |
| Voto de cabresto (grupos organizados) | Limite de 5 aprovações/dia por usuário | -50 pts por infração |
| Spam de comentários | Cooldown de 30s entre comentários | -20 pts por spam |
| Auto-aprovação | Logs de auditoria com IP + timestamp | -500 pts + banimento |
| Farming de indicações | Indicação só conta se indicada pessoa ficar 30 dias ativa | Indicação cancelada |
| Multi-contas | Fingerprint do navegador + email + telefone | Todas contas zeradas |

### Sistema de cooldown:
- ⏱️ Ações repetitivas têm **cooldown** (ex: 1 curso a cada 4h)
- ⏱️ Moderação: **máx 10 ações/dia** por usuário
- ⏱️ Badges: **revisão semanal** pra detectar exploits

---

## 🎯 Missões Semanais

Toda segunda-feira, o sistema gera missões personalizadas:

| Tipo | Exemplo | Recompensa |
|------|---------|------------|
| 📚 Educacional | "Crie 1 curso sobre meio ambiente" | +50 pts |
| 🗳️ Cidadania | "Vote em 3 propostas de governança" | +30 pts |
| 🛡️ Moderação | "Avalie 5 cursos na fila" | +75 pts |
| 🔍 Fiscalização | "Valide 2 denúncias" | +100 pts |
| 🤝 Comunidade | "Ajude 3 novatos no fórum" | +40 pts |

### Bônus de conclusão:
- ✅ 3/5 missões = +20 pts
- ✅ 5/5 missões = +50 pts + badge "Dedicado da Semana"

---

## 🏅 Leaderboard

### Mensal
- 🏆 Top 1 do mês: badge "Cidadão do Mês" + +500 pts
- 🥈 Top 2-10: badge "Destaque Mensal" + +200 pts
- 🥉 Top 11-50: badge "Contribuidor" + +100 pts

### Reset:
- ⚠️ Leaderboard reseta todo dia 1º
- ⚠️ Pontos totais **NUNCA** resetam
- ⚠️ Badges mensais são **sazonais** (não acumulam)

---

## 📊 Transparência

Todos os dados são públicos em:
- 🔍 **Auditoria**: `/api/audit/log` (qualquer um consulta)
- 📈 **Stats globais**: `/api/stats/global`
- 👤 **Perfil público**: `/perfil/{username}` mostra pontos, badges, nível

---

## 🔄 Revisão

Este documento é revisado a cada **3 meses** pela comunidade.

Sugestões? Abra uma **issue** com a tag `gamificacao`.

---

*Última atualização: 01/07/2026*
