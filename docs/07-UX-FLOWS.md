# UX e fluxos prioritários

## Princípios

- informação crítica antes de decoração;
- reduzir troca de contexto;
- ações frequentes próximas do objeto;
- confirmação apenas para ações irreversíveis ou de alto impacto;
- feedback imediato após ações;
- teclado e foco visível;
- cores nunca como único indicador;
- sidebar com rolagem independente em telas menores;
- estado do plantão sempre visível sem ocupar espaço excessivo.

## Arquitetura de informação

```text
Operação
├─ Dashboard
├─ Incidentes
│  ├─ Ativos
│  ├─ Resolvidos
│  └─ Histórico
├─ Passagem de turno

Base operacional
├─ Unidades
├─ Circuitos
├─ Operadoras
└─ Contatos

Configuração
├─ Severidades
├─ Templates
├─ Usuários e acessos
└─ Operação

Governança
├─ Auditoria
└─ Saúde do sistema (admin)
```

## Fluxo 1 — Criar incidente

### Sprint 1 — fluxo canônico

1. Incidentes → “Novo incidente”.
2. Informar título/resumo curto.
3. Informar recurso/serviço afetado.
4. Selecionar severidade: `CRITICAL`, `HIGH`, `MEDIUM` ou `LOW`.
5. Selecionar tipo de impacto: `OUTAGE` ou `DEGRADATION`.
6. Informar sintomas/descrição.
7. Informar início do incidente.
8. Validar campos e limites antes do envio.
9. Salvar.
10. Em sucesso, navegar para o detalhe do incidente criado.

Estados obrigatórios do formulário:

- inicial;
- inválido com mensagens associadas aos campos;
- envio/loading sem duplo submit;
- erro recuperável mantendo os dados digitados;
- sucesso com navegação para o detalhe.

Tenant e ator não são campos editáveis do formulário. Na Sprint 1 são resolvidos por contexto técnico controlado do backend; autenticação, memberships e troca de tenant entram no incremento próprio.

Critério UX da Sprint 1: permitir criação rápida e inequívoca sem exigir cadastro de base operacional ainda não implementado.

### Modelo alvo do produto

Quando base operacional, correlação e severidades configuráveis estiverem disponíveis, o fluxo evolui para:

1. Dashboard/Incidentes → “Novo incidente”.
2. Selecionar unidade ou localizar por código/nome.
3. Sistema mostra circuitos e incidentes ativos correlatos.
4. Selecionar severidade e origem.
5. Informar detecção e resumo.
6. Sistema alerta possível duplicidade antes de salvar.
7. Salvar.
8. Usuário cai na página do incidente.

Critério UX alvo: não exigir que o analista navegue à base operacional para copiar dados já relacionados à unidade.

## Fluxo 2 — Atualizar incidente

Na página do incidente:

- cabeçalho compacto com ID, unidade/recurso, severidade, status e idade;
- situação atual em destaque;
- timeline cronológica;
- formulário rápido de atualização;
- protocolos vinculados;
- próximos passos;
- ações de estado separadas de edição textual.

## Fluxo 3 — Normalizar

1. “Registrar normalização”.
2. Exigir horário de restauração.
3. Informar resolução e ação corretiva.
4. Gerar prévia do comunicado.
5. Confirmar resolução.
6. Timeline recebe evento; incidente passa para `RESOLVED`.

O sistema não deve esconder o incidente imediatamente após resolver; exibir feedback e permitir revisar o registro.

## Fluxo 4 — Passagem de turno — Sprint 4

### Preview

1. Acessar “Passagem de turno”.
2. Sistema calcula a janela atual usando a timezone/configuração do tenant.
3. Carregar preview via API, sem persistir draft.
4. Exibir incidentes ativos e incidentes normalizados no turno.
5. Permitir observação geral opcional.
6. Não permitir que o usuário remova/adicione manualmente incidentes ao snapshot na Sprint 4; a seleção é autoridade do backend.

Estados obrigatórios:

- loading;
- preview vazio;
- preview com itens;
- erro recuperável;
- sessão expirada;
- sem permissão.

### Finalização

1. Usuário com permissão aciona “Finalizar passagem”.
2. UI apresenta confirmação curta explicando que o snapshot finalizado é imutável.
3. Botão fica desabilitado durante envio para impedir duplo submit.
4. Backend recalcula o snapshot e persiste nova versão.
5. Em sucesso, UI navega para a versão finalizada e mostra versão, autoria e horário.
6. Em `409` de concorrência, UI informa que outra finalização ocorreu e oferece recarregar o handover mais recente.
7. Viewer não vê ação de finalizar, mas a API continua sendo a autoridade e retorna 403 se chamada diretamente.

### Consulta

- “Passagem de turno” abre o handover mais recente quando existir;
- versões anteriores ficam acessíveis por histórico/link;
- o conteúdo do snapshot nunca é atualizado visualmente a partir do estado atual do incidente;
- empty state: “Nenhuma passagem de turno finalizada para esta operação.”

## Dashboard — Sprint 4

A primeira versão usa somente agregados sustentados pelo domínio executável:

- incidentes ativos;
- incidentes críticos ativos;
- incidentes normalizados na janela atual.

Abaixo dos cards: fila ativa ordenada por severidade e antiguidade (`started_at`).

Cards funcionam como atalhos/filtros para a lista de incidentes. Não serão exibidas métricas de SLA, “aguardando terceiro” ou atraso de atualização enquanto essas regras não estiverem implementadas e medidas.

### Estados

- loading com skeleton/placeholder estável;
- vazio sem incidentes ativos;
- erro recuperável com retry;
- 401/sessão expirada;
- 403/sem permissão.

O dashboard não deve depender somente de cor para severidade/status e precisa manter navegação por teclado.

## Acessibilidade

Meta: WCAG 2.2 AA nos fluxos principais.

- contraste adequado;
- labels associados;
- navegação por teclado;
- `aria-live` para toasts importantes;
- focus management em modais;
- evitar timers que removam conteúdo crítico;
- ícone + texto para status, não somente cor.

## Estados vazios e erro

Todo módulo deve prever:

- loading;
- vazio real;
- vazio por filtro;
- erro recuperável;
- sem permissão;
- sessão expirada;
- conflito de edição.

## Responsividade

- desktop/notebook: experiência principal;
- 1024px: sidebar recolhível e conteúdo sem clipping;
- tablet: consulta e atualizações simples;
- mobile: funcionalidade básica, sem promessa de paridade no MVP.
