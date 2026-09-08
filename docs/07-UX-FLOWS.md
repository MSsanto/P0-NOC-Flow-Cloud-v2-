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

1. Dashboard → “Novo incidente”.
2. Selecionar unidade ou localizar por código/nome.
3. Sistema mostra circuitos e incidentes ativos correlatos.
4. Selecionar severidade e origem.
5. Informar detecção e resumo.
6. Sistema alerta possível duplicidade antes de salvar.
7. Salvar.
8. Usuário cai na página do incidente com CTA de “Registrar alerta inicial”.

Critério UX: não exigir que o analista navegue à base operacional para copiar dados já relacionados à unidade.

## Fluxo 2 — Atualizar incidente

Na página do incidente:

- cabeçalho compacto com ID, unidade, severidade, status e idade;
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

## Fluxo 4 — Passagem de turno

1. Acessar “Passagem de turno”.
2. Sistema calcula turno atual pela timezone/configuração.
3. Prévia inclui incidentes abertos + relevantes resolvidos no turno.
4. Analista adiciona observações e ajusta próximos passos permitidos.
5. Finalizar gera snapshot versionado.
6. Próximo turno consulta versão final, sem depender do estado futuro das telas.

## Dashboard

Cards devem funcionar como atalhos:

- incidentes ativos;
- sem atualização dentro da meta;
- aguardando terceiro;
- em monitoramento;
- resolvidos no turno.

Abaixo dos cards: fila priorizada por severidade + envelhecimento.

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