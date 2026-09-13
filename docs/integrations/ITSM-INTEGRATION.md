# Integração ITSM — P0 NOC Flow Cloud v2

**Status:** backlog pós-v1.0 / P4 — Integrações

## Objetivo
Integrar incidentes do NOC Flow com ferramentas externas sem acoplar o domínio a um fornecedor.

## Arquitetura

```text
Incident Service
  -> ITSM Integration Service
  -> ITSMProvider
      -> PlusoftProvider
      -> GLPIProvider
      -> ZammadProvider
      -> ServiceNowProvider (futuro)
      -> JiraServiceManagementProvider (futuro)
      -> MockProvider
```

O NOC Flow mantém o incidente interno como fonte principal. A integração externa guarda a correlação por sistema e protocolo externo.

## Regras
- criação idempotente;
- eventos repetidos não podem abrir tickets duplicados;
- falha do ITSM externo não pode apagar ou reverter o incidente interno;
- retry limitado e observável;
- credenciais ficam em configuração segura;
- toda sincronização registra resultado e timestamp;
- conflitos de status seguem política explícita.

## Contrato mínimo
- criar ticket;
- atualizar ticket;
- resolver ticket;
- consultar ticket;
- health check.

## Plusoft
O adapter Plusoft será específico e configurável. A implementação depende da documentação e dos endpoints efetivamente liberados na instância contratada.

## GLPI / Zammad
GLPI ou Zammad serão usados como opção de laboratório/demo com dados sintéticos, permitindo validar o padrão de integração antes de depender de uma plataforma empresarial.

## Dados mínimos de correlação
- incident_id;
- tenant_id;
- external_system;
- external_ticket_id;
- external_status;
- last_synced_at;
- sync_status.

## Critérios de aceite
1. Um incidente elegível cria exatamente um ticket externo.
2. O protocolo externo aparece no detalhe do incidente.
3. Atualizações podem ser propagadas ao ITSM quando suportado.
4. Normalização pode encerrar o ticket externo quando suportado.
5. Reprocessamento não cria duplicidade.
6. Falha temporária usa retry controlado.
7. Testes automatizados usam MockProvider.
8. O provider pode ser trocado por configuração sem alterar regras do domínio.

## Sequenciamento sugerido
1. ITSMProvider + MockProvider;
2. persistência da correlação externa;
3. GLPI ou Zammad para demo;
4. abertura/atualização/normalização;
5. Plusoft após validar o contrato real da API;
6. adapters adicionais conforme necessidade.
