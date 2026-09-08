# Product Vision

## Visão

**Para equipes de NOC que precisam acompanhar incidentes de conectividade com consistência, o NOC Flow Cloud v2 é uma plataforma operacional que centraliza contexto, padroniza comunicações, registra a evolução do incidente e preserva a continuidade entre turnos. Diferentemente de planilhas e fluxos dispersos, a plataforma mantém uma timeline auditável, multiusuário e segregada por operação.**

## Personas

### Analista NOC

Precisa agir rápido, localizar dados sem trocar de tela desnecessariamente, gerar textos corretos e deixar contexto claro para o próximo plantão.

### Líder/Supervisor

Precisa enxergar o estado do plantão, incidentes envelhecidos, pendências, qualidade dos registros e histórico de decisões.

### Administrador da operação

Precisa parametrizar unidades, circuitos, operadoras, contatos, severidades, templates e regras sem editar código.

## Jobs to be Done

- Quando um alerta chega, quero transformá-lo em um incidente estruturado sem redigitar os mesmos dados.
- Quando um incidente evolui, quero registrar atualização mantendo contexto e histórico.
- Quando o serviço volta, quero registrar normalização e preservar a causa/ação corretiva informada.
- Quando meu turno termina, quero gerar uma passagem de turno confiável com pendências e próximos passos.
- Quando procuro um evento antigo, quero encontrar a timeline por unidade, protocolo, circuito, severidade ou período.
- Quando administro outra operação, quero configurar o comportamento sem criar um fork do produto.

## Proposta de valor

1. **Contexto em um lugar:** incidente, unidade, circuitos, protocolos, próximos passos e timeline.
2. **Padronização:** templates versionados e campos estruturados.
3. **Continuidade:** handover gerado a partir do estado real dos incidentes.
4. **Auditabilidade:** quem fez o quê, quando e em qual operação.
5. **Configurabilidade:** operação definida por dados, não por hard-code.
6. **Integração progressiva:** manual primeiro; APIs e adapters depois.

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

## Não objetivos do MVP

- substituir monitoramento;
- substituir ITSM;
- executar comandos em rede;
- enviar mensagens automaticamente sem revisão;
- IA tomando decisão de severidade ou fechamento;
- construir billing de SaaS.

## North Star conceitual

**Incidentes operacionais com contexto completo e continuidade de turno.**

A métrica será definida após o MVP, evitando inventar baseline antes de haver uso mensurável.