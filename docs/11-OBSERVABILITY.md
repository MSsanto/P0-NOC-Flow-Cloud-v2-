# Observabilidade

## Objetivos

Responder rapidamente:

- a API está saudável?
- qual endpoint está falhando?
- qual request produziu o erro?
- há degradação de latência?
- um tenant específico está enfrentando erro sem expor seus dados?
- uma integração externa está instável?
- um deploy recente introduziu regressão?

## Princípios

- observabilidade deve ajudar diagnóstico, não apenas acumular logs;
- correlação entre request, trace, log e erro deve ser preservada;
- telemetria não deve carregar secrets nem conteúdo operacional desnecessário;
- instrumentação deve permanecer o mais vendor-neutral possível;
- alertas devem ser acionáveis e evitar ruído excessivo.

## Logs estruturados

Campos mínimos:

- timestamp UTC;
- level;
- service;
- environment;
- request_id;
- trace_id quando disponível;
- route;
- method;
- status_code;
- duration_ms;
- actor_id pseudonimizado/ID interno quando necessário;
- tenant_id interno quando necessário e permitido;
- error_code;
- application_version/commit_sha quando disponível.

Não registrar tokens, secrets, senhas, bodies completos por padrão, CNPJ/telefone/contato ou texto operacional desnecessário.

## Métricas

- requests por endpoint/status;
- latência p50/p95/p99;
- error rate;
- DB connection pool;
- incident creations/updates/resolutions como métricas agregadas do sistema, sem dados sensíveis;
- falhas de integração;
- filas futuras;
- restart/crash do container quando disponível;
- resultado de health/readiness.

## Tracing

OpenTelemetry é a camada preferencial para instrumentação vendor-neutral.

No alvo Azure, a preferência é exportar a telemetria para Azure Monitor/Application Insights usando a distribuição OpenTelemetry suportada para Python, evitando acoplamento desnecessário da camada de domínio ao SDK de observabilidade.

Regras:

- `trace_id` deve acompanhar requests relevantes;
- dependências externas e acesso ao banco devem ser correlacionáveis quando a instrumentação suportar;
- nenhum span deve incluir payload sensível sem necessidade explícita;
- sampling poderá ser adotado somente quando houver volume que justifique e sem comprometer investigação de erros críticos.

## Health

### `/health/live`

Indica que o processo está vivo.

- não depende de serviços externos lentos;
- falha somente quando o processo não consegue continuar servindo;
- é apropriado para liveness probes.

### `/health/ready`

Indica que a API está pronta para receber tráfego.

- pode validar dependências essenciais como banco;
- deve falhar quando a aplicação não consegue atender requests corretamente;
- é apropriado para readiness probes e smoke pós-deploy.

Health endpoints não devem retornar secrets, strings de conexão ou detalhes internos desnecessários.

## Azure Monitor / Application Insights

Quando a fase cloud estiver ativa:

- Application Insights recebe traces, métricas e telemetria da aplicação;
- Log Analytics centraliza consulta e retenção de logs;
- dashboards devem priorizar disponibilidade, erro, latência e dependências;
- `service.name`, ambiente e versão devem permitir distinguir deployments;
- conexão com Application Insights deve vir de configuração externa/secret, nunca hard-coded.

## Alertas de plataforma

Quando a infraestrutura correspondente existir:

- aumento sustentado de 5xx;
- readiness falhando;
- latência acima da meta;
- banco indisponível;
- falha repetida de deployment;
- crash/restart anormal;
- consumo anormal de CPU/memória;
- ausência inesperada de telemetria de um serviço crítico.

Cada alerta deve registrar, quando possível:

- ambiente;
- serviço;
- condição;
- janela observada;
- severidade;
- link para evidência/log/dashboard;
- ação inicial esperada.

## Deploy e correlação

Para facilitar investigação de regressões:

- cada deployment deve ser identificável por commit SHA/tag;
- logs e telemetria devem incluir versão quando possível;
- falhas iniciadas após um deploy devem poder ser comparadas com a revisão anterior;
- smoke e health pós-deploy devem produzir evidência verificável.

## Auditoria ≠ log técnico

Audit log registra ações de negócio/governança e possui retenção/política própria. Logs técnicos servem diagnóstico e não substituem auditoria.

Eventos de auditoria não devem depender exclusivamente de Application Insights/Log Analytics para sua persistência de negócio.
