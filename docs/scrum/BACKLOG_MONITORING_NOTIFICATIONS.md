# Backlog — Monitoring & Notifications

**Horizonte:** P4 / pós-v1.0  
**Status:** refinado para planejamento futuro  
**Documento técnico:** [`../integrations/MONITORING-NOTIFICATIONS.md`](../integrations/MONITORING-NOTIFICATIONS.md)

## Épico

Integrar o NOC Flow a fontes de monitoramento e canais de notificação para reduzir trabalho manual, evitar falsos positivos e acelerar a resposta operacional.

Fluxo de referência:

```text
Zabbix → evento normalizado → PENDING → janela configurável → revalidação
       → incidente automático → NotificationService → WhatsApp
```

## Itens

- **P4-011 — Adapter Zabbix**: ingerir/consultar eventos e convertê-los para contrato interno.
- **P4-012 — Persistência de eventos**: registrar `monitoring_events`, correlação e estado `PENDING`.
- **P4-013 — Janela de persistência**: threshold configurável; referência inicial de 20 minutos.
- **P4-014 — Revalidação**: confirmar que a falha continua ativa antes de criar incidente.
- **P4-015 — Criação automática**: criar exatamente um incidente por evento confirmado.
- **P4-016 — NotificationService**: abstração de canais e provider mock para CI.
- **P4-017 — Evolution API**: provider WhatsApp para laboratório/demo controlado.
- **P4-018 — Provider oficial futuro**: alternativa para implantação empresarial.
- **P4-019 — Normalização**: notificar recuperação sem duplicidade.
- **P4-020 — Observabilidade**: métricas de eventos, criação automática, envios e falhas.

## User Stories

### US-MON-001 — Ingerir eventos do Zabbix
Receber eventos do Zabbix por adapter próprio e transformá-los em eventos internos normalizados.

### US-MON-002 — Confirmar queda persistente
Manter a falha como pendente e somente promover após o threshold configurado. Recuperação anterior encerra o evento sem incidente.

### US-MON-003 — Criar incidente automaticamente
Após confirmação da persistência, criar um único incidente vinculado ao evento de monitoramento.

### US-NOT-001 — Notificar abertura
Enviar notificação quando o incidente automático for criado, sem acoplar regra de negócio ao provider.

### US-NOT-002 — Notificar normalização
Enviar aviso de recuperação vinculado ao incidente correspondente.

### US-NOT-003 — Provider Evolution API
Disponibilizar Evolution API como provider substituível para ambiente de laboratório/demo.

## Casos de aceite essenciais

- queda de 8 min com threshold de 20 min → nenhum incidente;
- queda maior ou igual ao threshold → exatamente um incidente;
- recovery antes do threshold → nenhum incidente e nenhuma notificação;
- evento repetido → nenhuma duplicação;
- processamento repetido → nenhuma duplicação;
- provider de mensagem indisponível → incidente permanece válido e envio registra falha;
- recovery após abertura → normalização correlacionada;
- provider mock permite CI sem dependência externa.

## Dependências

Este épico deve ser implementado após estabilização de timeline/lifecycle, tenant/auth, observabilidade e estratégia de jobs assíncronos. Ele não altera o escopo das Sprints 1–6 atuais.
