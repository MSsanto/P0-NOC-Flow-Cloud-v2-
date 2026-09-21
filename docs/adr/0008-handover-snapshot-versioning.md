# ADR-0008 — Handover como snapshot versionado

**Status:** Accepted  
**Data:** 2026-09-21

## Contexto

A passagem de turno precisa preservar o contexto recebido no momento da transferência, sem depender do estado futuro dos incidentes. Uma consulta dinâmica dos incidentes atuais não é suficiente porque o conteúdo pode mudar depois da troca de turno, destruindo a evidência do que foi efetivamente entregue.

A Sprint 4 também precisa evitar complexidade prematura com edição colaborativa de rascunhos, locks ou um subsistema de workflow próprio.

## Decisão

O handover será modelado como **snapshot versionado e imutável após finalização**.

### Preview

O preview é calculado server-side para o tenant e turno ativos. Ele não é persistido como rascunho na Sprint 4.

O preview inclui, no mínimo:

- incidentes ativos;
- incidentes relevantes resolvidos no turno;
- severidade e status no instante da geração;
- situação/última atualização disponível;
- protocolos e próximo passo quando existirem no modelo implementado;
- observações informadas pelo operador;
- ator e timestamps resolvidos pelo backend.

### Finalização

Finalizar um handover cria, em uma única transação:

1. um registro `handover`;
2. os `handover_items` correspondentes ao snapshot;
3. metadados de autoria, tenant, janela de turno e versão.

O cliente não é autoridade para `tenant_id`, autor, timestamps ou versão.

### Versionamento

Um handover finalizado nunca é alterado.

Se for necessário corrigir ou complementar uma passagem já finalizada, uma nova versão é criada para a mesma janela de turno, preservando as versões anteriores.

A versão é monotônica dentro da combinação tenant + janela de turno.

### Shift

Na Sprint 4, a janela de turno é calculada pela configuração/timezone do tenant. Não será criada uma entidade persistente `Shift` apenas para representar calendário enquanto não existir necessidade adicional comprovada.

### Concorrência

A criação de nova versão precisa ser protegida por constraint/transação para impedir duas finalizações com a mesma versão. Em disputa concorrente, uma requisição deve falhar com conflito explícito em vez de sobrescrever histórico.

### Isolamento

Todas as consultas e escritas são tenant-scoped pelo contexto autenticado. IDs de handover de outro tenant não podem ser enumerados pelo usuário comum.

## Contrato funcional da Sprint 4

Fluxo previsto:

1. consultar preview;
2. revisar observações;
3. finalizar snapshot;
4. consultar handover mais recente ou versão específica.

Não haverá update/delete de handover finalizado na Sprint 4.

## Permissões alvo

Permissões explícitas a introduzir no incremento:

- `handover:read`;
- `handover:finalize`.

Matriz alvo:

| Role | read | finalize |
|---|---:|---:|
| Admin | ✓ | ✓ |
| Supervisor | ✓ | ✓ |
| Operator | ✓ | ✓ |
| Viewer | ✓ | — |

Roles externas continuam sem autoridade; as permissions são derivadas da membership interna.

## Consequências

### Positivas

- preserva evidência da troca de turno;
- evita alteração retroativa;
- simplifica auditoria;
- reduz dependência do estado atual de Incident;
- mantém a Sprint 4 pequena sem persistência de draft.

### Custos

- snapshot duplica alguns dados operacionais deliberadamente;
- correções geram nova versão em vez de update;
- consultas históricas precisam escolher explicitamente a versão.

## Alternativas rejeitadas

### Handover como query dinâmica

Rejeitado porque o conteúdo mudaria retroativamente conforme os incidentes evoluíssem.

### Draft persistente editável

Adiado porque adicionaria locking, ownership de edição e lifecycle adicional sem necessidade demonstrada para o primeiro incremento.

### Copiar a timeline inteira

Rejeitado por duplicação excessiva. O snapshot guarda os campos necessários para continuidade; a timeline original continua sendo a fonte histórica detalhada do incidente.
