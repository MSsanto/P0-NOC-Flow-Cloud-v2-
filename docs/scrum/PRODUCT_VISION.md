# Product Vision — P0 NOC Flow Cloud v2

## Visão

**Para equipes de NOC que precisam acompanhar incidentes de conectividade com consistência, o NOC Flow Cloud v2 é uma plataforma operacional que centraliza contexto, padroniza comunicações, registra a evolução do incidente e preserva a continuidade entre turnos. Diferentemente de planilhas e fluxos dispersos, a plataforma mantém uma timeline auditável, multiusuário e segregada por operação.**

## Problema

Operações de NOC frequentemente distribuem o contexto de um incidente entre monitoramento, ITSM, planilhas, mensagens e memória do analista. Isso aumenta risco de duplicidade, inconsistência, perda de contexto na troca de turno e retrabalho.

## Personas

### Analista NOC
Precisa agir rapidamente, localizar dados sem alternar entre múltiplas fontes, gerar comunicações consistentes e deixar contexto claro para o próximo plantão.

### Líder / Supervisor
Precisa acompanhar estado do plantão, incidentes envelhecidos, pendências, qualidade dos registros e histórico de decisões.

### Administrador da operação
Precisa parametrizar unidades, circuitos, operadoras, contatos, severidades, templates e regras sem editar código.

## Jobs to be Done

- transformar um alerta em incidente estruturado sem redigitação desnecessária;
- registrar evolução mantendo contexto e histórico;
- registrar normalização e preservar causa/ação corretiva informada;
- gerar passagem de turno confiável com pendências e próximos passos;
- localizar eventos históricos por unidade, protocolo, circuito, severidade ou período;
- configurar operações diferentes sem criar forks do produto.

## Proposta de valor

1. **Contexto em um lugar:** incidente, unidade, circuitos, protocolos, próximos passos e timeline.
2. **Padronização:** templates versionados e campos estruturados.
3. **Continuidade:** handover gerado a partir do estado real dos incidentes.
4. **Auditabilidade:** quem fez o quê, quando e em qual operação.
5. **Configurabilidade:** operação definida por dados, não por hard-code.
6. **Integração progressiva:** operação manual primeiro; APIs e adapters depois.

## MVP

O MVP deve permitir, com autenticação e dados fictícios:

- entrar em uma operação autorizada;
- consultar base de unidades/circuitos;
- criar incidente manualmente;
- registrar alerta inicial;
- adicionar atualizações;
- normalizar/resolver incidente;
- consultar timeline;
- gerar comunicado a partir de template;
- visualizar dashboard do plantão;
- gerar e salvar passagem de turno;
- consultar auditoria básica.

## Fora do escopo do MVP

- substituir sistemas de monitoramento;
- substituir ITSM;
- executar comandos em rede;
- enviar mensagens automaticamente sem revisão humana;
- usar IA para decidir severidade ou fechamento;
- construir billing de SaaS.

## North Star conceitual

**Incidentes operacionais com contexto completo e continuidade de turno.**

A métrica quantitativa será definida após o MVP, evitando baseline ou ganho de produtividade não medido.

## Restrições de portfólio

- somente dados fictícios no repositório público;
- nenhum secret, credencial ou dado corporativo real;
- desenvolvimento local não pode depender obrigatoriamente da Azure;
- decisões relevantes devem ser rastreáveis e documentadas.