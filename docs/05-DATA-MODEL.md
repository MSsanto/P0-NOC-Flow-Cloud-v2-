# Modelo de dados

## Objetivo

Definir o modelo físico vigente do NOC Flow Cloud v2 com foco em integridade, isolamento por tenant, rastreabilidade, migrations reproduzíveis e evolução compatível com o roadmap.

**Estado atual:** Sprint 3 concluída tecnicamente. O schema executável possui `tenants`, `users`, `tenant_memberships`, `incidents` e `incident_events`.

## Decisões vigentes

- SGBD: PostgreSQL 17.
- ORM: SQLAlchemy; migrations: Alembic.
- Estratégia multi-tenant: banco e schema compartilhados, `tenant_id` obrigatório nas tabelas operacionais.
- Timestamps persistidos em UTC (`timestamptz`).
- Dados operacionais usam UUID.
- Valores de domínio de baixa cardinalidade usam `varchar` + constraints/checks quando aplicável.
- O incidente representa o estado corrente; `incident_events` representa a trilha cronológica operacional.
- A timeline é append-only no fluxo suportado: não existe endpoint de update/delete de evento.
- Dados públicos/de portfólio devem ser exclusivamente sintéticos.

## ER — estado após Sprint 3

```mermaid
erDiagram
    TENANT ||--o{ TENANT_MEMBERSHIP : has
    USER ||--o{ TENANT_MEMBERSHIP : joins
    TENANT ||--o{ INCIDENT : owns
    TENANT ||--o{ INCIDENT_EVENT : owns
    INCIDENT ||--o{ INCIDENT_EVENT : contains

    TENANT {
        uuid id PK
        varchar slug UK
        varchar name
        varchar timezone
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    USER {
        uuid id PK
        varchar external_subject UK
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    TENANT_MEMBERSHIP {
        uuid tenant_id PK,FK
        uuid user_id PK,FK
        varchar role
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    INCIDENT {
        uuid id PK
        uuid tenant_id FK
        varchar title
        varchar affected_resource
        varchar severity
        varchar impact_type
        text symptoms
        varchar status
        timestamptz started_at
        varchar created_by_subject
        timestamptz created_at
        timestamptz updated_at
        integer version
    }

    INCIDENT_EVENT {
        uuid id PK
        uuid tenant_id FK
        uuid incident_id FK
        varchar event_type
        text message
        varchar actor_subject
        timestamptz occurred_at
    }
```

## `tenants`

| Campo | Regra principal |
|---|---|
| `id` | UUID, PK |
| `slug` | identificador único do tenant |
| `name` | nome do tenant |
| `timezone` | timezone IANA; default operacional UTC |
| `is_active` | flag de ativação |
| `created_at` / `updated_at` | timestamps de auditoria básica |

O tenant não deve ser removido fisicamente enquanto possuir dados operacionais relacionados.

## `users`

| Campo | Regra principal |
|---|---|
| `id` | UUID, PK |
| `external_subject` | identificador externo único do usuário autenticado |
| `is_active` | usuário precisa estar ativo para compor contexto autenticado |
| `created_at` / `updated_at` | timestamps de auditoria básica |

O sistema não armazena senha. O vínculo com o provedor de identidade é feito pelo `external_subject`.

## `tenant_memberships`

| Campo | Regra principal |
|---|---|
| `tenant_id` | PK composta; FK para `tenants` |
| `user_id` | PK composta; FK para `users` |
| `role` | `Admin | Supervisor | Operator | Viewer` |
| `is_active` | membership precisa estar ativa para conceder contexto |
| `created_at` / `updated_at` | timestamps de auditoria básica |

A autorização é resolvida internamente a partir desta tabela. Claims externos de role/group não substituem a membership persistida.

## `incidents`

| Campo | Regra principal |
|---|---|
| `id` | UUID, PK |
| `tenant_id` | obrigatório; FK para tenant |
| `title` | 3–120 caracteres |
| `affected_resource` | 2–120 caracteres |
| `severity` | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `impact_type` | `OUTAGE`, `DEGRADATION` |
| `symptoms` | 10–2000 caracteres |
| `status` | lifecycle do incidente |
| `started_at` | início do incidente; não futuro no momento de criação |
| `created_by_subject` | ator resolvido server-side |
| `created_at` / `updated_at` | timestamps |
| `version` | começa em 1 e incrementa em ações operacionais da Sprint 2 |

Estados de domínio atuais:

```text
OPEN
ACKNOWLEDGED
INVESTIGATING
MONITORING
RESOLVED
CLOSED
```

Na Sprint 2, a normalização suportada leva o incidente a `RESOLVED`. `CLOSED` permanece previsto para evolução posterior.

## `incident_events`

Criada na Sprint 2 para suportar US-004/005/006.

| Campo | Regra principal |
|---|---|
| `id` | UUID, PK |
| `tenant_id` | obrigatório e tenant-scoped |
| `incident_id` | incidente pai |
| `event_type` | tipo estável do evento |
| `message` | conteúdo opcional conforme evento |
| `actor_subject` | ator resolvido pelo backend |
| `occurred_at` | timestamp do evento |

Tipos implementados:

```text
INCIDENT_CREATED
INCIDENT_UPDATED
INCIDENT_NORMALIZED
```

Regras:
- evento de criação é gravado junto da criação do incidente;
- atualização operacional grava novo evento e incrementa `incident.version`;
- normalização grava novo evento, muda status para `RESOLVED` e incrementa `version`;
- persistência do incidente pai é materializada antes do evento correspondente dentro da transação, evitando violação de FK;
- eventos são retornados em ordem cronológica;
- nenhum fluxo HTTP suportado modifica ou remove eventos já gravados.

## Isolamento por tenant

Consultas de incidentes e timeline incluem o tenant do contexto server-side. O cliente não fornece `tenant_id` como autoridade.

A modelagem mantém `tenant_id` também em `incident_events` para permitir filtragem explícita, defesa em profundidade e futuras constraints compostas de pertencimento ao mesmo tenant.

## Índices e padrões de consulta

Os índices de incidentes priorizam consultas tenant-scoped por tempo e status. A Sprint 2 também executa filtros por:

- `status`;
- `severity`;
- intervalo de `started_at`;
- ordenação por `started_at` ou `updated_at`.

A timeline é consultada por `(tenant_id, incident_id)` e ordenada por `occurred_at`/identificador.

Novos índices só devem ser adicionados quando houver padrão de consulta demonstrado; excesso de índice aumenta custo de escrita.

## Paginação

A consulta avançada da Sprint 2 usa offset/limit por `page` e `page_size` (máximo 100), adequado ao volume da alpha. Cursor pagination permanece opção para evolução quando volume/concorrência justificarem.

## Estratégia de migrations

- cada alteração de schema possui migration explícita;
- migrations precisam ser determinísticas e reproduzíveis;
- mudanças destrutivas devem seguir expand/contract;
- produção futura deve preferir correção forward quando rollback implicar perda de dados;
- migrations e testes são executados contra PostgreSQL no CI;
- downgrade destrutivo é aceitável apenas em ambientes descartáveis e deve ser documentado.

A migration da Sprint 2 cria `incident_events` e preserva a integridade do histórico necessário ao incremento.

## Identidade e compatibilidade de histórico

`created_by_subject` e `actor_subject` preservam a identidade do ator resolvida pelo backend. Desde a Sprint 3, `users` e `tenant_memberships` fornecem o contexto confiável de autorização, enquanto os subjects já gravados continuam preservados no histórico operacional.

O provider demo permanece restrito a `development`/`test`; staging/produção exigem identidade externa validada.

## Modelo alvo do roadmap

```mermaid
erDiagram
    TENANT ||--o{ MEMBERSHIP : has
    USER ||--o{ MEMBERSHIP : joins
    TENANT ||--o{ SITE : owns
    SITE ||--o{ CIRCUIT : has
    CARRIER ||--o{ CIRCUIT : provides
    TENANT ||--o{ SEVERITY : defines
    TENANT ||--o{ INCIDENT : owns
    INCIDENT ||--o{ INCIDENT_EVENT : contains
    INCIDENT ||--o{ PROTOCOL_LINK : links
    TENANT ||--o{ TEMPLATE : defines
    TEMPLATE ||--o{ TEMPLATE_VERSION : versions
    INCIDENT ||--o{ COMMUNICATION : renders
    TENANT ||--o{ HANDOVER : owns
    HANDOVER ||--o{ HANDOVER_ITEM : snapshots
    TENANT ||--o{ AUDIT_EVENT : records
```

Entidades do roadmap não devem ser antecipadas no schema apenas por estarem previstas.

## Checklist para alterações futuras

Toda mudança de schema deve responder:

1. Qual história/requisito exige a alteração?
2. O isolamento por tenant permanece explícito?
3. Há risco de perda/corrupção de dados?
4. A migration é compatível com a aplicação durante rollout?
5. Existe necessidade de backfill?
6. Índices correspondem a consultas reais?
7. Existe estratégia de rollback/correção forward?
8. Histórico e auditoria são preservados?
9. Backend, Database, Security e PO precisam validar alguma mudança de regra?


## Modelo planejado da Sprint 4 — ainda não implementado

A Sprint 4 introduzirá `handovers` e `handover_items` somente após aprovação deste readiness. Esta seção é contrato de implementação, não descrição do schema já executável.

### `handovers`

| Campo | Regra planejada |
|---|---|
| `id` | UUID, PK |
| `tenant_id` | obrigatório; FK para `tenants` |
| `window_start` | timestamptz UTC; início calculado do turno |
| `window_end` | timestamptz UTC; fim calculado do turno |
| `version` | inteiro >= 1; monotônico por tenant + janela |
| `observations` | texto opcional; limite definido no contrato HTTP |
| `finalized_by_subject` | ator resolvido server-side |
| `finalized_at` | timestamptz UTC definido pelo servidor |
| `created_at` | timestamptz UTC |

Constraint obrigatória:

```text
UNIQUE (tenant_id, window_start, window_end, version)
```

Índices planejados:

- `(tenant_id, finalized_at DESC)` para handover mais recente;
- `(tenant_id, window_start DESC, version DESC)` para histórico por turno.

### `handover_items`

| Campo | Regra planejada |
|---|---|
| `id` | UUID, PK |
| `handover_id` | obrigatório; FK para `handovers` com cascade no ambiente descartável apenas via remoção do pai fora do fluxo HTTP |
| `incident_id` | obrigatório; FK para `incidents` |
| `title_snapshot` | cópia do título no instante da finalização |
| `affected_resource_snapshot` | cópia do recurso afetado |
| `severity_snapshot` | severidade no snapshot |
| `status_snapshot` | status no snapshot |
| `started_at_snapshot` | início do incidente |
| `last_event_message_snapshot` | último texto de evento disponível; nullable |
| `last_event_at_snapshot` | instante do último evento disponível; nullable |

Constraint obrigatória:

```text
UNIQUE (handover_id, incident_id)
```

### Atomicidade e concorrência

- `handover` e todos os `handover_items` são criados na mesma transação;
- a versão seguinte é calculada dentro da operação de finalização;
- a unique constraint é a defesa final contra corrida;
- colisão concorrente retorna conflito controlado e não faz retry silencioso que esconda a disputa;
- não existe update/delete HTTP de handover finalizado;
- não será criada tabela `shifts` na Sprint 4.

### Migration

A migration da Sprint 4 deve ser aditiva: criar as duas tabelas, constraints e índices sem alterar colunas existentes de incidentes. Não exige backfill.
