# Case técnico — NOC Flow Cloud

## Problema

Em operações de NOC, o contexto de um incidente costuma ficar espalhado entre monitoramento, ITSM, planilhas e mensagens. O NOC Flow concentra o registro operacional, a timeline e a passagem de turno.

## Decisões principais

### Monólito modular

Escolhi um monólito modular porque o projeto ainda não precisa do custo operacional de microserviços. Os módulos continuam separados por responsabilidade para permitir evolução posterior.

### PostgreSQL

Incidentes, eventos, memberships e handovers precisam de transações e integridade referencial. Por isso a aplicação principal usa PostgreSQL com SQLAlchemy e Alembic.

### Multi-tenancy

O tenant é resolvido no backend. O cliente não escolhe `tenant_id` como autoridade. A autorização combina identidade externa com memberships internas.

### Timeline append-only

Atualizações operacionais viram novos eventos em vez de editar histórico existente. Isso deixa a linha do tempo mais simples de auditar.

### Handover como snapshot

A passagem de turno é gravada como snapshot versionado. Uma alteração posterior no incidente não reescreve um handover já finalizado.

### Cloudflare para demo privada

A demo usa Cloudflare Access e um adapter Worker/D1 para manter custo e operação baixos. A arquitetura principal continua FastAPI/PostgreSQL.

## Qualidade

O pipeline cobre:

- lint e type-check;
- migrations em PostgreSQL;
- testes de backend e frontend;
- cobertura mínima do backend;
- auditoria de dependências;
- build de produção;
- smoke tests atravessando frontend, API e banco.

## Limites atuais

- a demo é privada;
- Azure ainda é destino de evolução;
- integrações com Zabbix, WhatsApp e ITSM ainda estão no backlog;
- não há benchmark de escala publicado.

## O que eu mudaria numa próxima versão

- instrumentaria OpenTelemetry mais cedo;
- avaliaria PostgreSQL Row-Level Security como camada adicional;
- separaria ainda melhor o adapter da demo Cloudflare do contrato principal;
- manteria menos documentação de processo e mais documentação próxima do código.
