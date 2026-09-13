# Monitoring & Notifications — Zabbix + WhatsApp

**Status:** backlog refinado / pós-v1.0  
**Prioridade de produto:** P4 — Integrações  
**Objetivo:** transformar eventos de monitoramento persistentes em incidentes auditáveis e notificações desacopladas, sem criar falso positivo por indisponibilidades transitórias.

## Visão do fluxo

```text
Zabbix
  ↓ API/Webhook
Monitoring Adapter
  ↓ evento normalizado
Event Correlation
  ↓
PENDING
  ↓ janela configurável (ex.: 20 min)
revalidação da condição
  ├─ recuperou → CANCELLED / sem incidente
  └─ continua indisponível
          ↓
     cria incidente
          ↓
   NotificationService
      ├─ Evolution API / WhatsApp Web (lab/demo controlado)
      └─ Meta WhatsApp Cloud API (provider oficial futuro)
```

## Regra inicial de persistência

A referência inicial de produto é **20 minutos de indisponibilidade contínua** antes da criação automática do incidente e do disparo da notificação.

A janela não deve ser codificada como constante de domínio. Ela deve ser configurável por operação/regra e poderá evoluir, por exemplo:

- `CRITICAL`: 5 min;
- `HIGH`: 20 min;
- `MEDIUM`: 30 min;
- `LOW`: somente registro/observação ou sem abertura automática.

A configuração final deverá passar por refinamento de Produto e Security antes da implementação.

## Estados mínimos do evento de monitoramento

```text
PENDING → CONFIRMED → INCIDENT_CREATED
   ↓
RECOVERED/CANCELLED
```

Campos candidatos para `monitoring_events`:

- `id`;
- `tenant_id`;
- `source` (`ZABBIX` inicialmente);
- `external_event_id`;
- `resource_key`;
- `problem_key`;
- `severity`;
- `first_seen_at`;
- `last_seen_at`;
- `recovered_at`;
- `state`;
- `threshold_seconds`;
- `incident_id`;
- `created_at` / `updated_at`.

O schema definitivo depende de Database Architecture e ADR/migration próprios.

## Regras de negócio

1. Um evento recebido não cria incidente imediatamente.
2. O evento é persistido como `PENDING` com `first_seen_at`.
3. O sistema não deve usar `sleep(1200)` dentro de request/processo web para implementar a janela de 20 min.
4. Um worker/scheduler durável identifica eventos cuja janela venceu.
5. Antes de promover o evento, o sistema confirma que a condição ainda está ativa usando a fonte de monitoramento ou estado atualizado recebido por webhook.
6. Se a condição tiver recuperado antes da janela, o evento é encerrado sem incidente e sem WhatsApp.
7. Se a condição persistir, o sistema cria um único incidente e vincula o evento a ele.
8. Processamento deve ser idempotente: retries, webhooks duplicados ou polling repetido não podem criar incidentes ou notificações duplicadas.
9. Recuperação posterior deve poder gerar evento de timeline e, quando configurado, notificação de normalização.
10. Toda persistência e consulta deve respeitar tenant scoping.

## Integração Zabbix

Criar uma porta de domínio, por exemplo `MonitoringProvider`, e um adapter `ZabbixMonitoringProvider`.

Responsabilidades do adapter:

- autenticar na API do Zabbix sem expor segredo ao frontend;
- obter/receber eventos relevantes;
- converter host/item/trigger/event em contrato interno normalizado;
- preservar `external_event_id` para idempotência e rastreabilidade;
- tratar timeout, indisponibilidade, retry e rate limiting quando aplicável;
- não transportar dados corporativos reais para fixtures ou documentação pública.

O domínio do NOC Flow não deve depender de objetos específicos do Zabbix.

## NotificationService

A regra de negócio deve depender de uma abstração, não de uma API de WhatsApp específica.

```text
NotificationService
  └─ NotificationProvider
       ├─ EvolutionWhatsAppProvider
       ├─ MetaWhatsAppCloudProvider
       ├─ MockNotificationProvider
       └─ outros providers futuros
```

Contrato candidato:

```text
send_incident_opened(notification)
send_incident_recovered(notification)
```

O resultado deve registrar pelo menos provider, destinatário lógico mascarado quando aplicável, timestamp, status, tentativa e correlação com incidente/evento, sem gravar tokens ou conteúdo sensível indevido.

## Evolution API

Uso aprovado arquiteturalmente como **provider de laboratório/demo controlado**, através de integração isolada.

Regras:

- conexão/instância e API key ficam em configuração externa/secret store;
- QR Code não deve ser persistido no repositório;
- número/contato real não deve aparecer em fixture pública;
- falha ou desconexão do WhatsApp não pode desfazer a criação do incidente;
- envio deve possuir timeout, retry limitado e idempotência;
- a implementação via WhatsApp Web/Baileys não deve ser tratada como canal oficial de produção do WhatsApp;
- produção formal deverá preferir provider oficialmente suportado e passar por Security/Legal/Compliance quando aplicável.

## Meta WhatsApp Cloud API

Manter como provider alternativo/oficial para evolução futura. Templates, consentimento, política comercial e custo devem ser avaliados no momento da implantação. A regra de negócio não deve mudar para trocar de provider.

## User Stories candidatas

### US-MON-001 — Ingerir evento do Zabbix

Como plataforma NOC, quero receber eventos normalizados do Zabbix para registrar indisponibilidades sem acoplar o domínio ao formato externo.

**Aceite:** evento possui tenant/contexto confiável, ID externo, recurso, severidade e timestamps; duplicata não cria novo evento lógico.

### US-MON-002 — Confirmar queda persistente

Como operador NOC, quero que quedas transitórias não gerem incidentes para reduzir falso positivo.

**Aceite:** evento permanece `PENDING`; somente após a janela configurada e revalidação positiva ele é promovido; recuperação anterior cancela a abertura.

### US-MON-003 — Criar incidente automaticamente

Como operador NOC, quero que uma indisponibilidade persistente gere um incidente automaticamente para reduzir trabalho manual.

**Aceite:** um único incidente tenant-scoped é criado, com origem/rastreabilidade do evento; retries não duplicam incidentes.

### US-NOT-001 — Notificar abertura no WhatsApp

Como operador/supervisor, quero receber uma notificação quando um incidente automático for criado para agir sem depender do dashboard aberto.

**Aceite:** NotificationService usa provider configurado; falha de mensagem não faz rollback do incidente; tentativa e resultado são auditáveis.

### US-NOT-002 — Notificar normalização

Como operador/supervisor, quero receber a normalização do incidente para saber que o recurso voltou sem consultar manualmente o sistema.

**Aceite:** recuperação correlaciona evento/incidente, não duplica mensagens e respeita preferências de canal.

### US-NOT-003 — Provider Evolution API

Como ambiente de laboratório/demo, quero enviar notificações via Evolution API para validar o fluxo WhatsApp sem acoplar o domínio ao provider.

**Aceite:** credenciais externas; health/status de instância tratável; timeout/retry/idempotência; provider substituível por configuração.

## Casos de teste obrigatórios

- DOWN por 8 min com threshold 20 min → nenhum incidente;
- DOWN por 20+ min → exatamente um incidente;
- evento duplicado do Zabbix → exatamente um evento lógico/incidente;
- worker executa duas vezes → sem duplicação;
- recovery no minuto 19 → nenhum incidente/WhatsApp;
- recovery após incidente → timeline/normalização vinculada;
- Evolution indisponível → incidente persiste e notification fica falha/retry, sem rollback;
- retry de envio → sem mensagem duplicada quando houver chave idempotente disponível no adapter;
- tentativa cross-tenant → bloqueada;
- segredo/token nunca aparece em log.

## Observabilidade

Métricas candidatas:

- eventos recebidos por provider;
- eventos `PENDING`;
- eventos cancelados por recuperação precoce;
- incidentes criados automaticamente;
- latência `first_seen → incident_created`;
- notificações enviadas/falhas/retries;
- disponibilidade dos providers externos.

Logs devem carregar `request_id`/`correlation_id`, `tenant_id`, `external_event_id` e `incident_id` quando existirem, sem secrets.

## Fora do primeiro incremento

- ações automáticas em equipamentos/rede;
- reinício/alteração automática de dispositivos;
- envio a clientes finais;
- decisões automáticas irreversíveis;
- IA/LLM decidindo abertura ou normalização;
- integração específica com dados de cliente real no repositório público.

## Dependências

Antes de implementar este épico, o projeto deve ter, no mínimo:

- lifecycle/timeline de incidente estável;
- idempotência e contrato de integração definidos;
- auth/tenant context confiáveis;
- observabilidade suficiente para diagnosticar jobs assíncronos;
- estratégia de secrets;
- revisão AppSec do adapter Zabbix e do provider de mensageria.

## Definition of Done adicional

Além da DoD geral do projeto:

- testes de idempotência e recuperação precoce verdes;
- nenhuma mensagem duplicada nos cenários testados;
- falha de provider externo não corrompe estado do incidente;
- logs sem tokens/números sensíveis desnecessários;
- documentação de configuração/rollback;
- provider mock disponível para CI;
- Evolution API não é requisito obrigatório para executar testes automatizados do core.
