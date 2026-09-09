# Requisitos

## Requisitos funcionais

### RF-001 — Autenticação
O sistema deve identificar o usuário por um provedor OIDC/OAuth2 e criar sessão segura.

### RF-002 — Autorização por operação
O usuário deve acessar somente operações às quais possui vínculo ativo.

### RF-003 — Papéis
Papéis mínimos: `platform_admin`, `tenant_admin`, `supervisor`, `analyst`, `viewer`.

### RF-004 — Base operacional
Administradores devem manter unidades, circuitos, operadoras, contatos, severidades e templates.

### RF-005 — Incidente
Analistas devem criar incidente com operação, unidade, severidade, origem, horário de detecção e descrição no modelo operacional alvo.

#### Recorte canônico da Sprint 1 — US-002

Para a Sprint 1 — Fundação Executável, a criação de incidente usa deliberadamente um recorte mínimo do domínio, sem antecipar base operacional, autenticação completa ou severidades configuráveis.

Campos obrigatórios recebidos pelo `POST /api/v1/incidents`:

- `title`: 3–120 caracteres;
- `affected_resource`: 2–120 caracteres;
- `severity`: `CRITICAL | HIGH | MEDIUM | LOW`;
- `impact_type`: `OUTAGE | DEGRADATION`;
- `symptoms`: 10–2000 caracteres;
- `started_at`: timestamp ISO-8601; não pode ser posterior ao momento do registro.

Campos definidos pelo sistema/contexto e que não são autoridade do body:

- `id`;
- `status`, inicialmente `OPEN`;
- `tenant_id` resolvido de contexto técnico autorizado/controlado;
- ator/criador resolvido pelo backend;
- `created_at` e `updated_at`.

Durante a Sprint 1, tenant e ator podem vir de um provider de desenvolvimento/demo explicitamente isolado e sintético. Isso não substitui OIDC, memberships e RBAC planejados para a Sprint 3.

A evolução para unidade/site, origem e severidade configurável ocorrerá por histórias e migrations posteriores. Os nomes e regras acima são o contrato canônico da US-002 e devem ser refletidos em OpenAPI, frontend, banco e testes da Sprint 1.

### RF-006 — Correlação
O sistema deve sinalizar possível duplicidade considerando tenant, unidade/circuito, tipo de evento, estado e janela temporal configurável.

### RF-007 — Timeline
Todo incidente deve possuir eventos ordenados e imutáveis quanto à autoria/hora original.

### RF-008 — Atualização
Analistas devem registrar situação atual, protocolo/ITSM, ação executada e próximo passo.

### RF-009 — Normalização
Incidentes devem poder ser resolvidos com horário, evidência textual, ação corretiva e comunicado de normalização.

### RF-010 — Reabertura
Usuário autorizado deve poder reabrir incidente resolvido, mantendo o histórico.

### RF-011 — Templates
Templates devem ser versionados e renderizados a partir de dados estruturados.

### RF-012 — Passagem de turno
O sistema deve gerar snapshot contendo incidentes abertos, incidentes relevantes resolvidos no turno, pendências e observações.

### RF-013 — Busca
Busca por unidade, identificador, protocolo, circuito, operadora, severidade, status e período.

### RF-014 — Dashboard
Exibir contagens e filas acionáveis do plantão, sem substituir a lista detalhada.

### RF-015 — Auditoria
Mudanças administrativas, de permissão e de estado do incidente devem gerar eventos de auditoria.

### RF-016 — Exportação
Exportações devem respeitar tenant, autorização e registro de auditoria.

### RF-017 — Demonstração
Deve existir seed exclusivamente sintético para ambiente de portfólio.

### RF-018 — API versionada
Endpoints públicos do produto devem iniciar em `/api/v1`.

## Requisitos não funcionais

### RNF-001 — Segurança
TLS em trânsito; segredos fora do repositório; princípio do menor privilégio.

### RNF-002 — Isolamento
Nenhuma consulta de negócio pode retornar dados de tenant não autorizado.

### RNF-003 — Auditabilidade
IDs, timestamps em UTC e identidade do ator devem ser preservados.

### RNF-004 — Desempenho
Meta inicial: p95 < 500 ms para leituras simples do MVP sob carga de demonstração. É meta, não SLA contratado.

### RNF-005 — Acessibilidade
Interface planejada para WCAG 2.2 AA nos fluxos principais.

### RNF-006 — Responsividade
Prioridade desktop/notebook; suporte funcional a tablet; mobile não será a superfície principal no MVP.

### RNF-007 — Observabilidade
Logs estruturados, correlation/request ID, métricas de erro/latência e health checks.

### RNF-008 — Resiliência
Operações de escrita devem usar transação quando alterarem múltiplas entidades relacionadas.

### RNF-009 — Manutenibilidade
Separação clara entre domínio, aplicação, infraestrutura e apresentação.

### RNF-010 — Portabilidade local
Ambiente local deve iniciar com ferramentas documentadas, sem assinatura Azure obrigatória.

### RNF-011 — Privacidade
Seeds, fixtures, exemplos e screenshots públicos devem conter somente dados fictícios.

### RNF-012 — Compatibilidade
Últimas versões estáveis dos principais navegadores Chromium e Firefox no momento do release.

## Regras de negócio essenciais

- todo incidente pertence a exatamente um tenant;
- toda unidade pertence a um tenant;
- um usuário pode pertencer a múltiplos tenants;
- todo evento operacional registra ator, instante UTC e tipo;
- normalização não apaga alertas/atualizações anteriores;
- exclusão física de incidente não faz parte do fluxo normal;
- templates usados em comunicado devem preservar a versão aplicada;
- handover é snapshot versionado, não uma query efêmera;
- severidade é configurável por tenant, mas deve possuir ordem de prioridade;
- horários exibidos usam timezone configurado da operação, enquanto persistência usa UTC.
