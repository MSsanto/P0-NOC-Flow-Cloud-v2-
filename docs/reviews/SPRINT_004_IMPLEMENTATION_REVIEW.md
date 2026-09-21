# Sprint 004 — Implementation Review

**Data:** 2026-09-21  
**Escopo:** review técnico/adversarial pré-merge  
**Issue:** #49  
**PR:** #50

## Objetivo

Verificar se a implementação da Sprint 4 segue o readiness/ADR-0008, preserva segurança multi-tenant e possui evidência suficiente antes do merge.

## Achados e correções durante a implementação

### I1 — Lint backend

O primeiro CI encontrou imports fora da ordem e linha acima do limite em testes.

**Ação:** imports/formatting corrigidos antes de prosseguir. O Ruff passou na rodada seguinte.

### I2 — Mock Angular desatualizado

A navegação passou a usar `AuthContextService.can()`, mas o stub de `AppComponent` não implementava o método.

**Ação:** stub atualizado com `can()` e novas permissions. Unit tests e build passaram na rodada seguinte.

### I3 — Evidência de least privilege de handover

A matriz previa Viewer com leitura e sem finalização, mas faltava um teste integrado explícito no novo fluxo.

**Ação:** adicionado teste comprovando preview permitido e finalize retornando 403 para Viewer.

### I4 — Evidência cross-tenant específica de handover

O repositório era tenant-scoped, mas faltava prova direta de que um UUID de handover de outro tenant não seria enumerável.

**Ação:** adicionado teste integrado que cria handover em outro tenant e exige 404/HANDOVER_NOT_FOUND.

### I5 — Defesa final contra corrida de versão

A migration contém UNIQUE por tenant/janela/versão e o repository traduz IntegrityError para conflito, mas faltava prova isolada da constraint.

**Ação:** adicionado teste PostgreSQL que tenta persistir duas versões idênticas e exige IntegrityError.

## Conformidade com ADR-0008

- [x] preview calculado e não persistido;
- [x] finalização recalcula itens server-side;
- [x] snapshot persistido e imutável;
- [x] correção cria nova versão;
- [x] sem update/delete HTTP de handover;
- [x] Shift permanece value object calculado;
- [x] janela usa timezone/configuração do tenant;
- [x] versão possui defesa transacional/constraint;
- [x] tenant/ator/versão/itens não são autoridade do cliente.

## Gates exigidos antes do merge

A rodada final do PR deve terminar verde em:

- CI;
- Frontend Foundation;
- Cloudflare Private UI;
- Private Demo Compose;
- Sprint 2 Functional Smoke;
- Sprint 4 Functional Smoke.

## Resultado

**APROVÁVEL PARA MERGE somente com o head final integralmente verde.**

Após o merge, deve existir uma nova rodada verde na `main`. Depois disso, não resta atividade técnica obrigatória da Sprint 4; resta apenas homologação humana da experiência e do perímetro privado.
