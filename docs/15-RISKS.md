# Registro de riscos

| ID | Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|---|
| R-01 | Vazamento entre tenants | Média | Crítico | tenant scoping central, policies, testes cross-tenant, revisão de queries |
| R-02 | Publicação acidental de dado corporativo | Média | Crítico | seeds sintéticos, checklist de PR, secret scan, revisão de screenshots |
| R-03 | Escopo crescer antes do MVP | Alta | Alto | backlog P1/P2, não objetivos explícitos, ADR para mudanças grandes |
| R-04 | Complexidade de auth atrasar vertical slice | Média | Médio | abstração de identity + provider demo controlado no desenvolvimento |
| R-05 | Microserviços prematuros | Baixa | Alto | modular monolith como decisão explícita |
| R-06 | UX ficar pesada como sistema ITSM genérico | Média | Alto | fluxos NOC prioritários, testes de usabilidade, progressive disclosure |
| R-07 | Modelo de incidentes não acomodar integrações | Média | Alto | timeline/eventos + adapters + IDs externos separados |
| R-08 | Templates permitirem XSS | Média | Alto | escaping, sanitização e formatos restritos |
| R-09 | Custos Azure desnecessários | Média | Médio | ambiente local, planos baratos, budget alerts, desligar recursos não usados |
| R-10 | Dependência forte de Azure | Baixa | Médio | domínio provider-neutral, OpenTelemetry, PostgreSQL padrão, containers |
| R-11 | Handover mudar retroativamente | Média | Alto | snapshot versionado e finalização imutável |
| R-12 | Concorrência entre analistas sobrescrever dados | Média | Alto | versionamento otimista + eventos append-only |
| R-13 | Logs conterem texto sensível | Média | Alto | logging allowlist, sem bodies por padrão |
| R-14 | Métricas de produtividade sem baseline | Alta | Médio | publicar somente métricas observadas/reproduzíveis |
| R-15 | Integração externa duplicar eventos | Alta em P4 | Alto | idempotency key, external event ID, correlation window |
| R-16 | Falha de migration durante deploy | Baixa/Média | Alto | migration CI, backup/restore, estratégia expand-contract quando necessário |

## Critérios de escalonamento

Risco `Crítico` bloqueia release enquanto não houver mitigação implementada ou aceitação documentada. Riscos que mudem arquitetura geram ADR.

## Revisão

Este arquivo deve ser revisado ao final de cada fase e quando surgir incidente/bug de classe nova.