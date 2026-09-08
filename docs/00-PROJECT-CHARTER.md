# Project Charter — P0 NOC Flow Cloud v2

## 1. Propósito

Transformar o conceito do NOC Flow em uma aplicação cloud colaborativa, segura e demonstrável em portfólio, mantendo o foco em reduzir fricção operacional sem automatizar decisões críticas de forma opaca.

## 2. Problema

Operações de NOC frequentemente espalham o contexto de um incidente entre monitoramento, ITSM, planilhas, mensagens e memória do analista. Isso aumenta o risco de duplicidade, inconsistência entre comunicados, perda de contexto na troca de turno e retrabalho para localizar dados de unidade, circuito e operadora.

## 3. Resultado esperado

Uma aplicação web que concentre contexto operacional e produza uma linha do tempo auditável desde a detecção até a normalização, com passagem de turno consistente e segregação por operação.

## 4. Objetivos P0

- definir visão, escopo e não escopo;
- definir domínio e estados de incidente;
- definir arquitetura e stack;
- definir estratégia multi-tenant;
- definir modelo lógico de dados;
- definir API v1;
- definir fluxos UX prioritários;
- definir requisitos de segurança e privacidade;
- definir estratégia de testes;
- definir arquitetura Azure e CI/CD;
- criar backlog priorizado e Definition of Done;
- registrar riscos e ADRs.

## 5. Critério de saída do P0

O P0 é considerado concluído quando:

1. os documentos principais estiverem versionados;
2. não existirem decisões arquiteturais essenciais em aberto para o primeiro incremento;
3. o MVP estiver claramente delimitado;
4. cada épico P1 tiver critérios de aceite;
5. o modelo de dados e os endpoints principais forem coerentes entre si;
6. segurança, segregação de tenant e auditoria tiverem abordagem definida;
7. a primeira fatia vertical implementável estiver identificada.

## 6. Stakeholders conceituais

- **Analista NOC:** opera incidentes e passagem de turno.
- **Líder/Supervisor:** acompanha operação, auditoria e indicadores.
- **Administrador da operação:** mantém cadastros, templates e permissões.
- **Administrador da plataforma:** mantém tenants e parâmetros globais.
- **Integrações:** monitoramento, ITSM e canais externos futuros.

## 7. Restrições

- repositório público: somente dados fictícios;
- nenhuma credencial ou dado corporativo real em código, documentação ou histórico;
- prioridade para soluções de baixo custo em ambiente de demonstração;
- desenvolvimento local deve funcionar sem depender da Azure;
- decisões críticas devem ser rastreáveis por ADR.

## 8. Métricas do produto

As métricas abaixo são metas futuras, não resultados já obtidos:

- tempo mediano entre registro e primeiro comunicado;
- percentual de incidentes com atualização dentro da janela definida;
- quantidade de duplicidades evitadas;
- percentual de handovers com incidentes abertos corretamente incluídos;
- erros de validação bloqueados antes de salvar;
- latência p95 da API em fluxos principais;
- taxa de falhas em produção/demonstração.

Não serão publicados ganhos percentuais de produtividade sem medição reproduzível.