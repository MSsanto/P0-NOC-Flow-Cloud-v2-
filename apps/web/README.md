# apps/web

Aplicação Angular do **NOC Flow Cloud v2**.

A fundação inicial é entregue pela EN-004 da Sprint 1 e estabelece routing, shell, environments, `HttpClient`, tratamento básico de erros, acessibilidade e testes unitários mínimos.

## Requisitos

- Node.js `>=22.22.3`
- npm 11 para geração/atualização do lockfile
- `package-lock.json` versionado para builds reproduzíveis com `npm ci`

## Desenvolvimento local

```bash
npm install --global npm@11
npm ci
npm start
```

Quando as dependências forem alteradas intencionalmente, atualizar o lockfile com npm 11 e revisar o diff antes de versionar. O lockfile da fundação foi gerado em ambiente limpo de CI e está versionado no repositório.

Por padrão, o ambiente de desenvolvimento consome a API em:

```text
http://localhost:8000/api/v1
```

Em produção, o frontend usa a base relativa:

```text
/api/v1
```

## Qualidade

```bash
npm run build
npm test
npm run lint
```

O workflow `Frontend Foundation` executa a mesma sequência em ambiente limpo e valida a reprodutibilidade das dependências.

> `lint` nesta fundação executa a checagem estrita do TypeScript. Uma ferramenta dedicada de lint poderá ser adicionada pelo fluxo de qualidade/DevOps sem alterar contratos de domínio.

## Estrutura inicial

```text
src/app/
  core/
    http/
  features/
    foundation/
  app.component.ts
  app.config.ts
  app.routes.ts
```

A evolução segue a arquitetura por features definida em `docs/03-ARCHITECTURE.md`.

## Limites

- autorização final pertence à API;
- tokens não devem ser persistidos em locais inseguros;
- regras críticas de domínio permanecem no backend;
- o frontend replica apenas validações necessárias à experiência do usuário;
- contratos da API não são alterados unilateralmente pelo frontend;
- APIs de negócio são consumidas sob `/api/v1`.
