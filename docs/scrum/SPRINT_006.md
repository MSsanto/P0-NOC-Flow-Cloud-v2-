# Sprint 006 — Azure & Release v1.0

**Status:** Planejamento futuro  
**Duração planejada:** 2 semanas  
**Release alvo:** `v1.0.0`  
**Sprint Goal:** publicar, endurecer e homologar a primeira versão estável do NOC Flow Cloud v2.

## Enablers de release

- EN-S6-01 ambientes development/test/staging/production;
- EN-S6-02 deploy Azure com arquitetura simples e custo controlado;
- EN-S6-03 pipeline com lint, build, testes, security checks, staging, smoke e aprovação;
- EN-S6-04 regression/E2E/smoke completos;
- EN-S6-05 security hardening final;
- EN-S6-06 documentação de deployment, rollback e operação;
- EN-S6-07 documentação de portfólio e screenshots;
- EN-S6-08 homologação final `v1.0.0`.

## Distribuição por especialistas

- **01 PO:** validar escopo final do MVP e critérios de release.
- **02 Architecture:** validar arquitetura implantada e desvios/ADRs.
- **03 UX/UI:** revisão final de consistência, acessibilidade e responsividade.
- **04 Frontend:** correções de release e configuração por ambiente.
- **05 Backend:** correções de release, configuração e migrations seguras.
- **06 Database:** migration/deploy/backup-restore de demonstração e revisão final.
- **07 QA:** regressão, E2E, API e smoke.
- **08 DevOps:** Azure, ambientes, CI/CD, rollback e observabilidade de produção.
- **09 Security:** hardening final e gate de vulnerabilidades.
- **10 Docs:** README, Architecture, API, Deployment, Security, changelog e portfólio.
- **11 Review:** code review final e dívida técnica crítica.
- **12 Release:** go/no-go e homologação v1.0.0.

## Tasks principais

TASK-PO-S6-01 aceite final MVP; TASK-ARC-S6-01 architecture conformance; TASK-UX-S6-01 accessibility/UX pass; TASK-FE-S6-01 env/release fixes; TASK-BE-S6-01 migrations/config/release fixes; TASK-DB-S6-01 deploy/backup checks; TASK-QA-S6-01 regression; TASK-QA-S6-02 E2E; TASK-QA-S6-03 smoke; TASK-DO-S6-01 Azure environments; TASK-DO-S6-02 deployment pipeline; TASK-DO-S6-03 rollback; TASK-SEC-S6-01 hardening; TASK-DOC-S6-01 portfolio/release docs; TASK-CR-S6-01 final review; TASK-REL-S6-01 go/no-go.

## Quality Gate v1.0.0

A release somente pode ser APROVADA quando:
- build e CI estiverem verdes;
- migrations forem validadas;
- smoke/E2E/regressão críticos passarem;
- nenhuma vulnerabilidade Critical/High permanecer aberta sem mitigação aprovada;
- nenhum BLOCKER de code review permanecer;
- documentação refletir o estado implantado;
- staging estiver validado;
- rollback/runbook estiver documentado;
- Release Manager registrar decisão APROVADA.
