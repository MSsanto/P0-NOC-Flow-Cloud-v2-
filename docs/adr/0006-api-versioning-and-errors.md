# ADR-0006 — Versionamento da API e contrato uniforme de erros

**Status:** Accepted  
**Data:** 2026-09-08

## Contexto

Frontend, backend, testes e integrações precisam evoluir sem depender de comportamentos acidentais da API. Além disso, operadores e suporte precisam correlacionar falhas sem expor detalhes internos ou dados sensíveis.

## Decisão

1. A API pública da aplicação usa versionamento principal na URL, iniciando em `/api/v1`.
2. Mudanças aditivas retrocompatíveis permanecem na mesma versão principal.
3. Mudanças incompatíveis exigem nova versão principal ou plano explícito de migração/depreciação.
4. O OpenAPI gerado pelo FastAPI é o contrato executável; documentação complementar não substitui o schema publicado.
5. Erros seguem Problem Details compatível com RFC 9457 e incluem um `code` estável e `request_id` para correlação.
6. Exceções internas são mapeadas na borda HTTP; stack traces, SQL, tokens e secrets nunca fazem parte da resposta ao cliente.
7. Recursos existentes em outro tenant podem resultar em `404` para usuários sem acesso, reduzindo enumeração cross-tenant.

## Formato base de erro

Campos mínimos: `type`, `title`, `status`, `detail`, `instance`, `code`, `request_id`.

Erros de validação podem acrescentar uma coleção `errors` com `field`, `code` e `message`.

## Alternativas consideradas

- versionamento apenas por header: rejeitado inicialmente por aumentar complexidade operacional e de debugging sem benefício proporcional neste estágio;
- retornar diretamente os erros padrão do framework: rejeitado porque acopla consumidores a detalhes de implementação e dificulta estabilidade do contrato;
- formato de erro próprio sem Problem Details: rejeitado por não oferecer vantagem relevante sobre um padrão amplamente reconhecido.

## Consequências

### Positivas

- contrato previsível para Angular, testes e integrações;
- evolução controlada da API;
- melhor observabilidade via `request_id`;
- menor risco de exposição de detalhes internos;
- tratamento programático por códigos estáveis.

### Custos e riscos

- handlers de exceção precisam ser mantidos de forma consistente;
- versões antigas, quando existirem consumidores reais, podem exigir período de convivência;
- códigos de erro passam a fazer parte do contrato e não devem ser alterados arbitrariamente.

## Referências

- `docs/03-ARCHITECTURE.md`
- `docs/06-API-CONTRACT.md`
