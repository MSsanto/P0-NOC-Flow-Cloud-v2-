const API_PREFIX = "/api/v1";
const TENANT_ID = "00000000-0000-4000-8000-000000000001";
const MAX_JSON_BODY_BYTES = 64 * 1024;

const SEVERITIES = new Set(["CRITICAL", "HIGH", "MEDIUM", "LOW"]);
const IMPACT_TYPES = new Set(["OUTAGE", "DEGRADATION"]);
const STATUSES = new Set([
  "OPEN",
  "ACKNOWLEDGED",
  "INVESTIGATING",
  "MONITORING",
  "RESOLVED",
  "CLOSED",
]);
const SORT_FIELDS = new Set(["started_at", "updated_at"]);
const SORT_ORDERS = new Set(["asc", "desc"]);
const ROLES = new Set(["Admin", "Supervisor", "Operator", "Viewer"]);

const ROLE_PERMISSIONS = Object.freeze({
  Admin: [
    "incident:read",
    "incident:create",
    "incident:update",
    "incident:normalize",
    "handover:read",
    "handover:finalize",
    "audit:read",
  ],
  Supervisor: [
    "incident:read",
    "incident:create",
    "incident:update",
    "incident:normalize",
    "handover:read",
    "handover:finalize",
    "audit:read",
  ],
  Operator: [
    "incident:read",
    "incident:create",
    "incident:update",
    "incident:normalize",
    "handover:read",
    "handover:finalize",
  ],
  Viewer: ["incident:read", "handover:read"],
});

let schemaReadyPromise;
const keyCache = new Map();

export class ApiProblem extends Error {
  constructor(status, title, detail, code, slug) {
    super(detail);
    this.name = "ApiProblem";
    this.status = status;
    this.title = title;
    this.detail = detail;
    this.code = code;
    this.slug = slug;
  }
}

function problem(status, title, detail, code, slug) {
  return new ApiProblem(status, title, detail, code, slug);
}

function resolveRequestId(candidate) {
  return typeof candidate === "string" &&
    /^[A-Za-z0-9._:-]{1,128}$/.test(candidate)
    ? candidate
    : crypto.randomUUID();
}

function responseHeaders(requestId, contentType = "application/json; charset=utf-8") {
  return {
    "content-type": contentType,
    "cache-control": "no-store",
    "x-request-id": requestId,
  };
}

function jsonResponse(data, requestId, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: responseHeaders(requestId),
  });
}

function problemResponse(error, requestId) {
  const body = {
    type: `https://nocflow.invalid/problems/${error.slug}`,
    title: error.title,
    status: error.status,
    detail: error.detail,
    code: error.code,
    request_id: requestId,
  };
  return new Response(JSON.stringify(body), {
    status: error.status,
    headers: responseHeaders(requestId, "application/problem+json; charset=utf-8"),
  });
}

function ensurePlainObject(value) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw problem(
      422,
      "Request validation failed",
      "The request body must be a JSON object.",
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }
  return value;
}

function assertAllowedKeys(value, allowedKeys) {
  const unexpected = Object.keys(value).filter((key) => !allowedKeys.has(key));
  if (unexpected.length > 0) {
    throw problem(
      422,
      "Request validation failed",
      `Unexpected field(s): ${unexpected.join(", ")}.`,
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }
}

function requiredString(value, field, minLength, maxLength) {
  if (typeof value !== "string") {
    throw problem(
      422,
      "Request validation failed",
      `${field} must be a string.`,
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }
  const normalized = value.trim();
  if (normalized.length < minLength || normalized.length > maxLength) {
    throw problem(
      422,
      "Request validation failed",
      `${field} must contain between ${minLength} and ${maxLength} characters.`,
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }
  return normalized;
}

function normalizeIsoDate(value, field) {
  if (typeof value !== "string" || value.trim() === "") {
    throw problem(
      422,
      "Request validation failed",
      `${field} must be a valid date-time.`,
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }

  let candidate = value.trim();
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,3})?)?$/.test(candidate)) {
    candidate += "Z";
  }
  const timestamp = Date.parse(candidate);
  if (!Number.isFinite(timestamp)) {
    throw problem(
      422,
      "Request validation failed",
      `${field} must be a valid date-time.`,
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }
  return new Date(timestamp).toISOString();
}

export function validateIncidentCreate(value, now = new Date()) {
  const payload = ensurePlainObject(value);
  const allowed = new Set([
    "title",
    "affected_resource",
    "severity",
    "impact_type",
    "symptoms",
    "started_at",
  ]);
  assertAllowedKeys(payload, allowed);

  const title = requiredString(payload.title, "title", 3, 120);
  const affectedResource = requiredString(
    payload.affected_resource,
    "affected_resource",
    2,
    120,
  );
  const symptoms = requiredString(payload.symptoms, "symptoms", 10, 2000);

  if (!SEVERITIES.has(payload.severity)) {
    throw problem(
      422,
      "Request validation failed",
      "severity is invalid.",
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }
  if (!IMPACT_TYPES.has(payload.impact_type)) {
    throw problem(
      422,
      "Request validation failed",
      "impact_type is invalid.",
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }

  const startedAt = normalizeIsoDate(payload.started_at, "started_at");
  if (Date.parse(startedAt) > now.getTime()) {
    throw problem(
      422,
      "Incident validation failed",
      "Incident start time cannot be in the future.",
      "INCIDENT_STARTED_AT_IN_FUTURE",
      "incident-started-at-in-future",
    );
  }

  return {
    title,
    affected_resource: affectedResource,
    severity: payload.severity,
    impact_type: payload.impact_type,
    symptoms,
    started_at: startedAt,
  };
}

export function validateIncidentUpdate(value) {
  const payload = ensurePlainObject(value);
  assertAllowedKeys(payload, new Set(["message"]));
  return { message: requiredString(payload.message, "message", 3, 2000) };
}

export function validateIncidentNormalize(value) {
  const payload = ensurePlainObject(value);
  assertAllowedKeys(payload, new Set(["note"]));
  if (payload.note === undefined || payload.note === null) {
    return { note: null };
  }
  return { note: requiredString(payload.note, "note", 3, 2000) };
}

function parsePositiveInteger(value, fallback, field, max) {
  if (value === null || value === "") {
    return fallback;
  }
  if (!/^\d+$/.test(value)) {
    throw problem(
      422,
      "Incident filter validation failed",
      `${field} must be a positive integer.`,
      "INCIDENT_INVALID_QUERY",
      "incident-invalid-query",
    );
  }
  const parsed = Number(value);
  if (parsed < 1 || (max !== undefined && parsed > max)) {
    throw problem(
      422,
      "Incident filter validation failed",
      max === undefined
        ? `${field} must be greater than or equal to 1.`
        : `${field} must be between 1 and ${max}.`,
      "INCIDENT_INVALID_QUERY",
      "incident-invalid-query",
    );
  }
  return parsed;
}

export function parseIncidentListQuery(url) {
  const params = url.searchParams;
  const status = params.get("status");
  const severity = params.get("severity");
  const sort = params.get("sort") ?? "started_at";
  const order = params.get("order") ?? "desc";

  if (status !== null && !STATUSES.has(status)) {
    throw problem(
      422,
      "Incident filter validation failed",
      "status is invalid.",
      "INCIDENT_INVALID_QUERY",
      "incident-invalid-query",
    );
  }
  if (severity !== null && !SEVERITIES.has(severity)) {
    throw problem(
      422,
      "Incident filter validation failed",
      "severity is invalid.",
      "INCIDENT_INVALID_QUERY",
      "incident-invalid-query",
    );
  }
  if (!SORT_FIELDS.has(sort) || !SORT_ORDERS.has(order)) {
    throw problem(
      422,
      "Incident filter validation failed",
      "sort or order is invalid.",
      "INCIDENT_INVALID_QUERY",
      "incident-invalid-query",
    );
  }

  const startedFromRaw = params.get("started_from");
  const startedToRaw = params.get("started_to");
  const startedFrom =
    startedFromRaw === null ? null : normalizeIsoDate(startedFromRaw, "started_from");
  const startedTo =
    startedToRaw === null ? null : normalizeIsoDate(startedToRaw, "started_to");

  if (
    startedFrom !== null &&
    startedTo !== null &&
    Date.parse(startedFrom) > Date.parse(startedTo)
  ) {
    throw problem(
      422,
      "Incident filter validation failed",
      "started_from cannot be after started_to.",
      "INCIDENT_INVALID_PERIOD",
      "incident-invalid-period",
    );
  }

  return {
    status,
    severity,
    started_from: startedFrom,
    started_to: startedTo,
    page: parsePositiveInteger(params.get("page"), 1, "page"),
    page_size: parsePositiveInteger(params.get("page_size"), 25, "page_size", 100),
    sort,
    order,
  };
}

export function permissionsForRole(role) {
  if (!ROLES.has(role)) {
    return [];
  }
  return [...ROLE_PERMISSIONS[role]];
}

async function readJson(request) {
  const contentLength = Number(request.headers.get("content-length") ?? "0");
  if (Number.isFinite(contentLength) && contentLength > MAX_JSON_BODY_BYTES) {
    throw problem(
      413,
      "Request body too large",
      "The request body exceeds the private demo limit.",
      "REQUEST_TOO_LARGE",
      "request-too-large",
    );
  }
  try {
    return await request.json();
  } catch {
    throw problem(
      422,
      "Request validation failed",
      "The request body must contain valid JSON.",
      "REQUEST_VALIDATION_FAILED",
      "request-validation-failed",
    );
  }
}

function decodeBase64UrlBytes(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
  const binary = atob(padded);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

function decodeJsonSegment(value) {
  const bytes = decodeBase64UrlBytes(value);
  return JSON.parse(new TextDecoder().decode(bytes));
}

async function fetchAccessKey(issuer, kid) {
  const cacheKey = `${issuer}|${kid}`;
  const existing = keyCache.get(cacheKey);
  if (existing) {
    return existing;
  }

  const certsUrl = `${issuer.replace(/\/$/, "")}/cdn-cgi/access/certs`;
  const response = await fetch(certsUrl);
  if (!response.ok) {
    throw problem(
      503,
      "Identity provider unavailable",
      "Cloudflare Access signing keys could not be loaded.",
      "IDENTITY_PROVIDER_UNAVAILABLE",
      "identity-provider-unavailable",
    );
  }
  const document = await response.json();
  const jwk = Array.isArray(document.keys)
    ? document.keys.find((candidate) => candidate.kid === kid)
    : undefined;
  if (!jwk) {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token signing key is not recognized.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }

  const key = await crypto.subtle.importKey(
    "jwk",
    jwk,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["verify"],
  );
  keyCache.set(cacheKey, key);
  return key;
}

async function authenticateAccessRequest(request) {
  const token = request.headers.get("cf-access-jwt-assertion");
  if (!token) {
    throw problem(
      401,
      "Authentication required",
      "A valid Cloudflare Access token is required.",
      "AUTH_REQUIRED",
      "authentication-required",
    );
  }

  const parts = token.split(".");
  if (parts.length !== 3) {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token is malformed.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }

  let header;
  let payload;
  try {
    header = decodeJsonSegment(parts[0]);
    payload = decodeJsonSegment(parts[1]);
  } catch {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token cannot be decoded.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }

  if (header.alg !== "RS256" || typeof header.kid !== "string") {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token algorithm is not accepted.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }

  let issuer;
  try {
    issuer = new URL(payload.iss);
  } catch {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token issuer is invalid.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }
  if (
    issuer.protocol !== "https:" ||
    !issuer.hostname.endsWith(".cloudflareaccess.com") ||
    (issuer.pathname !== "/" && issuer.pathname !== "")
  ) {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token issuer is not trusted.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }

  const nowSeconds = Math.floor(Date.now() / 1000);
  if (
    typeof payload.exp !== "number" ||
    payload.exp < nowSeconds - 30 ||
    (typeof payload.nbf === "number" && payload.nbf > nowSeconds + 30)
  ) {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token is expired or not active yet.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }
  if (payload.aud === undefined || payload.aud === null) {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token audience is missing.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }

  const key = await fetchAccessKey(issuer.origin, header.kid);
  const signature = decodeBase64UrlBytes(parts[2]);
  const data = new TextEncoder().encode(`${parts[0]}.${parts[1]}`);
  const verified = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5",
    key,
    signature,
    data,
  );
  if (!verified) {
    throw problem(
      401,
      "Invalid authentication token",
      "The Cloudflare Access token signature is invalid.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }

  const tokenEmail =
    typeof payload.email === "string" ? payload.email.trim().toLowerCase() : "";
  const headerEmail =
    request.headers
      .get("cf-access-authenticated-user-email")
      ?.trim()
      .toLowerCase() ?? "";
  const email = tokenEmail || headerEmail;
  if (!email || (tokenEmail && headerEmail && tokenEmail !== headerEmail)) {
    throw problem(
      401,
      "Invalid authentication token",
      "The authenticated identity email is unavailable or inconsistent.",
      "AUTH_INVALID_TOKEN",
      "invalid-authentication-token",
    );
  }

  return {
    email,
    subject: typeof payload.sub === "string" ? payload.sub : email,
  };
}

async function ensureSchema(env) {
  if (!env.DB) {
    throw problem(
      503,
      "Datastore unavailable",
      "The D1 binding is not available.",
      "DATASTORE_UNAVAILABLE",
      "datastore-unavailable",
    );
  }

  if (!schemaReadyPromise) {
    schemaReadyPromise = env.DB
      .batch([
        env.DB.prepare(`
          CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            slug TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
          )
        `),
        env.DB.prepare(`
          CREATE TABLE IF NOT EXISTS tenant_memberships (
            tenant_id TEXT NOT NULL,
            email TEXT NOT NULL,
            external_subject TEXT,
            role TEXT NOT NULL CHECK (role IN ('Admin','Supervisor','Operator','Viewer')),
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            PRIMARY KEY (tenant_id, email),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
          )
        `),
        env.DB.prepare(`
          CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            title TEXT NOT NULL,
            affected_resource TEXT NOT NULL,
            severity TEXT NOT NULL CHECK (severity IN ('CRITICAL','HIGH','MEDIUM','LOW')),
            impact_type TEXT NOT NULL CHECK (impact_type IN ('OUTAGE','DEGRADATION')),
            symptoms TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
              status IN ('OPEN','ACKNOWLEDGED','INVESTIGATING','MONITORING','RESOLVED','CLOSED')
            ),
            started_at TEXT NOT NULL,
            created_by_subject TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
          )
        `),
        env.DB.prepare(`
          CREATE TABLE IF NOT EXISTS incident_events (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            incident_id TEXT NOT NULL,
            event_type TEXT NOT NULL CHECK (
              event_type IN ('INCIDENT_CREATED','INCIDENT_UPDATED','INCIDENT_NORMALIZED')
            ),
            message TEXT,
            actor_subject TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
          )
        `),
        env.DB.prepare(
          "CREATE INDEX IF NOT EXISTS idx_incidents_tenant_started ON incidents(tenant_id, started_at DESC)",
        ),
        env.DB.prepare(
          "CREATE INDEX IF NOT EXISTS idx_incidents_tenant_status ON incidents(tenant_id, status)",
        ),
        env.DB.prepare(
          "CREATE INDEX IF NOT EXISTS idx_incidents_tenant_severity ON incidents(tenant_id, severity)",
        ),
        env.DB.prepare(
          "CREATE INDEX IF NOT EXISTS idx_events_tenant_incident ON incident_events(tenant_id, incident_id, occurred_at)",
        ),
        env.DB.prepare(`
          CREATE TABLE IF NOT EXISTS handovers (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            window_start TEXT NOT NULL,
            window_end TEXT NOT NULL,
            version INTEGER NOT NULL,
            observations TEXT,
            finalized_by_subject TEXT NOT NULL,
            finalized_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE (tenant_id, window_start, window_end, version),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
          )
        `),
        env.DB.prepare(`
          CREATE TABLE IF NOT EXISTS handover_items (
            id TEXT PRIMARY KEY,
            handover_id TEXT NOT NULL,
            incident_id TEXT NOT NULL,
            title_snapshot TEXT NOT NULL,
            affected_resource_snapshot TEXT NOT NULL,
            severity_snapshot TEXT NOT NULL,
            status_snapshot TEXT NOT NULL,
            started_at_snapshot TEXT NOT NULL,
            last_event_message_snapshot TEXT,
            last_event_at_snapshot TEXT,
            UNIQUE (handover_id, incident_id),
            FOREIGN KEY (handover_id) REFERENCES handovers(id),
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
          )
        `),
        env.DB.prepare(`
          CREATE TABLE IF NOT EXISTS audit_events (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            actor_subject TEXT NOT NULL,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT,
            request_id TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
          )
        `),
        env.DB.prepare(
          "CREATE INDEX IF NOT EXISTS idx_handovers_tenant_finalized ON handovers(tenant_id, finalized_at DESC)",
        ),
        env.DB.prepare(
          "CREATE INDEX IF NOT EXISTS idx_audit_tenant_occurred ON audit_events(tenant_id, occurred_at DESC)",
        ),
      ])
      .then(async () => {
        const now = new Date().toISOString();
        await env.DB.prepare(
          `INSERT OR IGNORE INTO tenants(id, slug, name, is_active, created_at)
           VALUES (?, 'private-demo', 'NOC Flow Private Demo', 1, ?)`,
        )
          .bind(TENANT_ID, now)
          .run();
      })
      .catch((error) => {
        schemaReadyPromise = undefined;
        throw error;
      });
  }
  return schemaReadyPromise;
}

async function resolveRequestContext(env, request) {
  const identity = await authenticateAccessRequest(request);
  await ensureSchema(env);
  const now = new Date().toISOString();

  await env.DB.prepare(`
    INSERT INTO tenant_memberships(
      tenant_id, email, external_subject, role, is_active, created_at
    )
    SELECT ?, ?, ?, 'Admin', 1, ?
    WHERE NOT EXISTS (
      SELECT 1 FROM tenant_memberships WHERE tenant_id = ?
    )
  `)
    .bind(TENANT_ID, identity.email, identity.subject, now, TENANT_ID)
    .run();

  const membership = await env.DB.prepare(`
    SELECT email, external_subject, role, is_active
    FROM tenant_memberships
    WHERE tenant_id = ? AND email = ?
  `)
    .bind(TENANT_ID, identity.email)
    .first();

  if (!membership || Number(membership.is_active) !== 1 || !ROLES.has(membership.role)) {
    throw problem(
      403,
      "Tenant access denied",
      "The authenticated identity is not authorized for the active tenant.",
      "TENANT_ACCESS_DENIED",
      "tenant-access-denied",
    );
  }

  return {
    tenant_id: TENANT_ID,
    actor_subject: identity.email,
    external_subject: identity.subject,
    role: membership.role,
    permissions: permissionsForRole(membership.role),
  };
}

function requirePermission(context, permission) {
  if (!context.permissions.includes(permission)) {
    throw problem(
      403,
      "Permission denied",
      "The authenticated identity does not have permission for this action.",
      "AUTH_FORBIDDEN",
      "permission-denied",
    );
  }
}

function mapIncident(row) {
  return {
    id: row.id,
    title: row.title,
    affected_resource: row.affected_resource,
    severity: row.severity,
    impact_type: row.impact_type,
    symptoms: row.symptoms,
    status: row.status,
    started_at: row.started_at,
    created_at: row.created_at,
    updated_at: row.updated_at,
    version: Number(row.version),
  };
}

function mapEvent(row) {
  return {
    id: row.id,
    incident_id: row.incident_id,
    event_type: row.event_type,
    message: row.message ?? null,
    actor_subject: row.actor_subject,
    occurred_at: row.occurred_at,
  };
}

function auditStatement(env, context, requestId, action, resourceType, resourceId, now) {
  return env.DB.prepare(`
    INSERT INTO audit_events(
      id, tenant_id, actor_subject, action, resource_type, resource_id, request_id, occurred_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    crypto.randomUUID(),
    context.tenant_id,
    context.actor_subject,
    action,
    resourceType,
    resourceId,
    requestId,
    now,
  );
}

function currentShiftWindow(now = new Date()) {
  const current = new Date(now);
  const anchor = new Date(current);
  anchor.setUTCHours(6, 0, 0, 0);
  if (current < anchor) {
    anchor.setUTCDate(anchor.getUTCDate() - 1);
  }
  const elapsed = current.getTime() - anchor.getTime();
  const slot = Math.floor(elapsed / (12 * 60 * 60 * 1000));
  const start = new Date(anchor.getTime() + slot * 12 * 60 * 60 * 1000);
  const end = new Date(start.getTime() + 12 * 60 * 60 * 1000);
  return { window_start: start.toISOString(), window_end: end.toISOString() };
}

async function listHandoverItems(env, context, window) {
  const result = await env.DB.prepare(`
    SELECT i.*
    FROM incidents i
    WHERE i.tenant_id = ?
      AND (
        i.status NOT IN ('RESOLVED','CLOSED')
        OR i.id IN (
          SELECT incident_id
          FROM incident_events
          WHERE tenant_id = ?
            AND event_type = 'INCIDENT_NORMALIZED'
            AND occurred_at >= ?
            AND occurred_at < ?
        )
      )
    ORDER BY
      CASE i.severity
        WHEN 'CRITICAL' THEN 0
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        ELSE 3
      END,
      i.started_at ASC
  `).bind(
    context.tenant_id,
    context.tenant_id,
    window.window_start,
    window.window_end,
  ).all();

  const items = [];
  for (const incident of result.results ?? []) {
    const latest = await env.DB.prepare(`
      SELECT message, occurred_at
      FROM incident_events
      WHERE tenant_id = ? AND incident_id = ?
      ORDER BY occurred_at DESC, id DESC
      LIMIT 1
    `).bind(context.tenant_id, incident.id).first();
    items.push({
      incident_id: incident.id,
      title: incident.title,
      affected_resource: incident.affected_resource,
      severity: incident.severity,
      status: incident.status,
      started_at: incident.started_at,
      last_event_message: latest?.message ?? null,
      last_event_at: latest?.occurred_at ?? null,
    });
  }
  return items;
}

async function dashboardSummary(env, context) {
  requirePermission(context, "incident:read");
  const window = currentShiftWindow();
  const activeResult = await env.DB.prepare(`
    SELECT *
    FROM incidents
    WHERE tenant_id = ? AND status NOT IN ('RESOLVED','CLOSED')
    ORDER BY
      CASE severity
        WHEN 'CRITICAL' THEN 0
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        ELSE 3
      END,
      started_at ASC
  `).bind(context.tenant_id).all();
  const items = (activeResult.results ?? []).map(mapIncident);
  const resolved = await env.DB.prepare(`
    SELECT COUNT(DISTINCT incident_id) AS total
    FROM incident_events
    WHERE tenant_id = ?
      AND event_type = 'INCIDENT_NORMALIZED'
      AND occurred_at >= ?
      AND occurred_at < ?
  `).bind(context.tenant_id, window.window_start, window.window_end).first();
  return {
    active_count: items.length,
    critical_active_count: items.filter((item) => item.severity === "CRITICAL").length,
    resolved_in_shift_count: Number(resolved?.total ?? 0),
    shift: window,
    items,
  };
}

async function handoverPreview(env, context) {
  requirePermission(context, "handover:read");
  const window = currentShiftWindow();
  return {
    ...window,
    generated_at: new Date().toISOString(),
    items: await listHandoverItems(env, context, window),
  };
}

function mapHandoverItem(row) {
  return {
    incident_id: row.incident_id,
    title: row.title_snapshot,
    affected_resource: row.affected_resource_snapshot,
    severity: row.severity_snapshot,
    status: row.status_snapshot,
    started_at: row.started_at_snapshot,
    last_event_message: row.last_event_message_snapshot ?? null,
    last_event_at: row.last_event_at_snapshot ?? null,
  };
}

async function getHandoverById(env, context, id) {
  requirePermission(context, "handover:read");
  const row = await env.DB.prepare(`
    SELECT *
    FROM handovers
    WHERE tenant_id = ? AND id = ?
  `).bind(context.tenant_id, id).first();
  if (!row) {
    throw problem(
      404,
      "Handover not found",
      "The requested handover was not found in the active tenant.",
      "HANDOVER_NOT_FOUND",
      "handover-not-found",
    );
  }
  const itemsResult = await env.DB.prepare(`
    SELECT *
    FROM handover_items
    WHERE handover_id = ?
    ORDER BY started_at_snapshot ASC, id ASC
  `).bind(row.id).all();
  return {
    id: row.id,
    version: Number(row.version),
    window_start: row.window_start,
    window_end: row.window_end,
    observations: row.observations ?? null,
    finalized_by_subject: row.finalized_by_subject,
    finalized_at: row.finalized_at,
    items: (itemsResult.results ?? []).map(mapHandoverItem),
  };
}

async function finalizeHandover(env, context, request, requestId) {
  requirePermission(context, "handover:finalize");
  const payload = ensurePlainObject(await readJson(request));
  assertAllowedKeys(payload, new Set(["observations"]));
  const observations =
    payload.observations === undefined || payload.observations === null || payload.observations === ""
      ? null
      : requiredString(payload.observations, "observations", 3, 4000);
  const window = currentShiftWindow();
  const items = await listHandoverItems(env, context, window);
  const versionRow = await env.DB.prepare(`
    SELECT MAX(version) AS version
    FROM handovers
    WHERE tenant_id = ? AND window_start = ? AND window_end = ?
  `).bind(context.tenant_id, window.window_start, window.window_end).first();
  const version = Number(versionRow?.version ?? 0) + 1;
  const id = crypto.randomUUID();
  const now = new Date().toISOString();

  const statements = [
    env.DB.prepare(`
      INSERT INTO handovers(
        id, tenant_id, window_start, window_end, version, observations,
        finalized_by_subject, finalized_at, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      id,
      context.tenant_id,
      window.window_start,
      window.window_end,
      version,
      observations,
      context.actor_subject,
      now,
      now,
    ),
    ...items.map((item) =>
      env.DB.prepare(`
        INSERT INTO handover_items(
          id, handover_id, incident_id, title_snapshot, affected_resource_snapshot,
          severity_snapshot, status_snapshot, started_at_snapshot,
          last_event_message_snapshot, last_event_at_snapshot
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        crypto.randomUUID(),
        id,
        item.incident_id,
        item.title,
        item.affected_resource,
        item.severity,
        item.status,
        item.started_at,
        item.last_event_message,
        item.last_event_at,
      ),
    ),
    auditStatement(env, context, requestId, "handover.finalized", "handover", id, now),
  ];
  try {
    await env.DB.batch(statements);
  } catch {
    throw problem(
      409,
      "Handover version conflict",
      "Another handover version was finalized concurrently. Reload and try again.",
      "HANDOVER_VERSION_CONFLICT",
      "handover-version-conflict",
    );
  }
  return getHandoverById(env, context, id);
}

async function handoverHistory(env, context, url) {
  requirePermission(context, "handover:read");
  const page = parsePositiveInteger(url.searchParams.get("page"), 1, "page");
  const pageSize = parsePositiveInteger(url.searchParams.get("page_size"), 25, "page_size", 100);
  const offset = (page - 1) * pageSize;
  const [count, list] = await env.DB.batch([
    env.DB.prepare("SELECT COUNT(*) AS total FROM handovers WHERE tenant_id = ?")
      .bind(context.tenant_id),
    env.DB.prepare(`
      SELECT id, version, window_start, window_end, finalized_by_subject, finalized_at
      FROM handovers
      WHERE tenant_id = ?
      ORDER BY finalized_at DESC, id DESC
      LIMIT ? OFFSET ?
    `).bind(context.tenant_id, pageSize, offset),
  ]);
  return {
    items: list.results ?? [],
    page,
    page_size: pageSize,
    total: Number(count.results?.[0]?.total ?? 0),
  };
}

async function latestHandover(env, context) {
  requirePermission(context, "handover:read");
  const row = await env.DB.prepare(`
    SELECT id
    FROM handovers
    WHERE tenant_id = ?
    ORDER BY finalized_at DESC, id DESC
    LIMIT 1
  `).bind(context.tenant_id).first();
  if (!row) {
    throw problem(
      404,
      "Handover not found",
      "No handover exists in the active tenant.",
      "HANDOVER_NOT_FOUND",
      "handover-not-found",
    );
  }
  return getHandoverById(env, context, row.id);
}

async function listAuditEvents(env, context, url) {
  requirePermission(context, "audit:read");
  const page = parsePositiveInteger(url.searchParams.get("page"), 1, "page");
  const pageSize = parsePositiveInteger(url.searchParams.get("page_size"), 25, "page_size", 100);
  const action = url.searchParams.get("action");
  const resourceType = url.searchParams.get("resource_type");
  const predicates = ["tenant_id = ?"];
  const bindings = [context.tenant_id];
  if (action) {
    predicates.push("action = ?");
    bindings.push(action);
  }
  if (resourceType) {
    predicates.push("resource_type = ?");
    bindings.push(resourceType);
  }
  const where = predicates.join(" AND ");
  const offset = (page - 1) * pageSize;
  const [count, list] = await env.DB.batch([
    env.DB.prepare(`SELECT COUNT(*) AS total FROM audit_events WHERE ${where}`).bind(...bindings),
    env.DB.prepare(`
      SELECT id, actor_subject, action, resource_type, resource_id, request_id, occurred_at
      FROM audit_events
      WHERE ${where}
      ORDER BY occurred_at DESC, id DESC
      LIMIT ? OFFSET ?
    `).bind(...bindings, pageSize, offset),
  ]);
  return {
    items: list.results ?? [],
    page,
    page_size: pageSize,
    total: Number(count.results?.[0]?.total ?? 0),
  };
}

async function getRequiredIncident(env, tenantId, incidentId) {
  const row = await env.DB.prepare(`
    SELECT *
    FROM incidents
    WHERE tenant_id = ? AND id = ?
  `)
    .bind(tenantId, incidentId)
    .first();
  if (!row) {
    throw problem(
      404,
      "Incident not found",
      "The requested incident was not found in the active tenant.",
      "INCIDENT_NOT_FOUND",
      "incident-not-found",
    );
  }
  return row;
}

async function listIncidents(env, context, url) {
  requirePermission(context, "incident:read");
  const query = parseIncidentListQuery(url);
  const predicates = ["tenant_id = ?"];
  const bindings = [context.tenant_id];

  if (query.status !== null) {
    predicates.push("status = ?");
    bindings.push(query.status);
  }
  if (query.severity !== null) {
    predicates.push("severity = ?");
    bindings.push(query.severity);
  }
  if (query.started_from !== null) {
    predicates.push("started_at >= ?");
    bindings.push(query.started_from);
  }
  if (query.started_to !== null) {
    predicates.push("started_at <= ?");
    bindings.push(query.started_to);
  }

  const where = predicates.join(" AND ");
  const offset = (query.page - 1) * query.page_size;
  const direction = query.order === "asc" ? "ASC" : "DESC";
  const sort = query.sort === "updated_at" ? "updated_at" : "started_at";

  const [countResult, listResult] = await env.DB.batch([
    env.DB.prepare(`SELECT COUNT(*) AS total FROM incidents WHERE ${where}`).bind(
      ...bindings,
    ),
    env.DB
      .prepare(
        `SELECT * FROM incidents
         WHERE ${where}
         ORDER BY ${sort} ${direction}
         LIMIT ? OFFSET ?`,
      )
      .bind(...bindings, query.page_size, offset),
  ]);

  const total = Number(countResult.results?.[0]?.total ?? 0);
  return {
    items: (listResult.results ?? []).map(mapIncident),
    page: query.page,
    page_size: query.page_size,
    total,
  };
}

async function listSimpleIncidents(env, context) {
  requirePermission(context, "incident:read");
  const result = await env.DB.prepare(`
    SELECT * FROM incidents
    WHERE tenant_id = ?
    ORDER BY started_at DESC
    LIMIT 100
  `)
    .bind(context.tenant_id)
    .all();
  return (result.results ?? []).map(mapIncident);
}

async function createIncident(env, context, request, requestId) {
  requirePermission(context, "incident:create");
  const payload = validateIncidentCreate(await readJson(request));
  const now = new Date().toISOString();
  const id = crypto.randomUUID();
  const eventId = crypto.randomUUID();

  await env.DB.batch([
    env.DB.prepare(`
      INSERT INTO incidents(
        id, tenant_id, title, affected_resource, severity, impact_type,
        symptoms, status, started_at, created_by_subject, created_at,
        updated_at, version
      ) VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, 1)
    `).bind(
      id,
      context.tenant_id,
      payload.title,
      payload.affected_resource,
      payload.severity,
      payload.impact_type,
      payload.symptoms,
      payload.started_at,
      context.actor_subject,
      now,
      now,
    ),
    env.DB.prepare(`
      INSERT INTO incident_events(
        id, tenant_id, incident_id, event_type, message, actor_subject, occurred_at
      ) VALUES (?, ?, ?, 'INCIDENT_CREATED', NULL, ?, ?)
    `).bind(eventId, context.tenant_id, id, context.actor_subject, now),
    auditStatement(env, context, requestId, "incident.created", "incident", id, now),
  ]);

  return mapIncident(await getRequiredIncident(env, context.tenant_id, id));
}

async function getIncident(env, context, incidentId) {
  requirePermission(context, "incident:read");
  return mapIncident(await getRequiredIncident(env, context.tenant_id, incidentId));
}

async function addIncidentUpdate(env, context, incidentId, request, requestId) {
  requirePermission(context, "incident:update");
  const payload = validateIncidentUpdate(await readJson(request));
  const current = await getRequiredIncident(env, context.tenant_id, incidentId);
  if (current.status === "RESOLVED" || current.status === "CLOSED") {
    throw problem(
      409,
      "Incident cannot be updated",
      "Resolved or closed incidents cannot receive operational updates.",
      "INCIDENT_NOT_ACTIVE",
      "incident-not-active",
    );
  }

  const now = new Date().toISOString();
  const eventId = crypto.randomUUID();
  await env.DB.batch([
    env.DB.prepare(`
      UPDATE incidents
      SET updated_at = ?, version = version + 1
      WHERE tenant_id = ? AND id = ?
    `).bind(now, context.tenant_id, incidentId),
    env.DB.prepare(`
      INSERT INTO incident_events(
        id, tenant_id, incident_id, event_type, message, actor_subject, occurred_at
      ) VALUES (?, ?, ?, 'INCIDENT_UPDATED', ?, ?, ?)
    `).bind(
      eventId,
      context.tenant_id,
      incidentId,
      payload.message,
      context.actor_subject,
      now,
    ),
    auditStatement(
      env,
      context,
      requestId,
      "incident.updated",
      "incident",
      incidentId,
      now,
    ),
  ]);

  return mapIncident(await getRequiredIncident(env, context.tenant_id, incidentId));
}

async function normalizeIncident(env, context, incidentId, request, requestId) {
  requirePermission(context, "incident:normalize");
  const payload = validateIncidentNormalize(await readJson(request));
  const current = await getRequiredIncident(env, context.tenant_id, incidentId);
  if (current.status === "RESOLVED" || current.status === "CLOSED") {
    throw problem(
      409,
      "Incident already normalized",
      "The incident is already normalized or closed.",
      "INCIDENT_ALREADY_NORMALIZED",
      "incident-already-normalized",
    );
  }

  const now = new Date().toISOString();
  const eventId = crypto.randomUUID();
  await env.DB.batch([
    env.DB.prepare(`
      UPDATE incidents
      SET status = 'RESOLVED', updated_at = ?, version = version + 1
      WHERE tenant_id = ? AND id = ?
    `).bind(now, context.tenant_id, incidentId),
    env.DB.prepare(`
      INSERT INTO incident_events(
        id, tenant_id, incident_id, event_type, message, actor_subject, occurred_at
      ) VALUES (?, ?, ?, 'INCIDENT_NORMALIZED', ?, ?, ?)
    `).bind(
      eventId,
      context.tenant_id,
      incidentId,
      payload.note,
      context.actor_subject,
      now,
    ),
    auditStatement(
      env,
      context,
      requestId,
      "incident.normalized",
      "incident",
      incidentId,
      now,
    ),
  ]);

  return mapIncident(await getRequiredIncident(env, context.tenant_id, incidentId));
}

async function listTimeline(env, context, incidentId) {
  requirePermission(context, "incident:read");
  await getRequiredIncident(env, context.tenant_id, incidentId);
  const result = await env.DB.prepare(`
    SELECT id, incident_id, event_type, message, actor_subject, occurred_at
    FROM incident_events
    WHERE tenant_id = ? AND incident_id = ?
    ORDER BY occurred_at ASC, id ASC
  `)
    .bind(context.tenant_id, incidentId)
    .all();
  return (result.results ?? []).map(mapEvent);
}

function validIncidentId(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
    value,
  );
}

function methodNotAllowed() {
  throw problem(
    405,
    "Method not allowed",
    "The requested method is not supported for this resource.",
    "METHOD_NOT_ALLOWED",
    "method-not-allowed",
  );
}

async function routeApi(request, env, requestId) {
  const url = new URL(request.url);
  const path = url.pathname;

  if (path === `${API_PREFIX}/health/live` || path === `${API_PREFIX}/health/ready`) {
    if (request.method !== "GET") methodNotAllowed();
    await ensureSchema(env);
    return jsonResponse({ status: "ok" }, requestId);
  }

  const context = await resolveRequestContext(env, request);

  if (path === `${API_PREFIX}/auth/me`) {
    if (request.method !== "GET") methodNotAllowed();
    return jsonResponse(
      {
        subject: context.actor_subject,
        tenant_id: context.tenant_id,
        roles: [context.role],
        permissions: [...context.permissions].sort(),
      },
      requestId,
    );
  }

  if (path === `${API_PREFIX}/dashboard/summary`) {
    if (request.method !== "GET") methodNotAllowed();
    return jsonResponse(await dashboardSummary(env, context), requestId);
  }

  if (path === `${API_PREFIX}/handovers/preview`) {
    if (request.method !== "GET") methodNotAllowed();
    return jsonResponse(await handoverPreview(env, context), requestId);
  }

  if (path === `${API_PREFIX}/handovers/latest`) {
    if (request.method !== "GET") methodNotAllowed();
    return jsonResponse(await latestHandover(env, context), requestId);
  }

  if (path === `${API_PREFIX}/handovers`) {
    if (request.method === "GET") {
      return jsonResponse(await handoverHistory(env, context, url), requestId);
    }
    if (request.method === "POST") {
      return jsonResponse(
        await finalizeHandover(env, context, request, requestId),
        requestId,
        201,
      );
    }
    methodNotAllowed();
  }

  const handoverDetailMatch = path.match(/^\/api\/v1\/handovers\/([^/]+)$/);
  if (handoverDetailMatch) {
    if (request.method !== "GET") methodNotAllowed();
    const handoverId = handoverDetailMatch[1];
    if (!validIncidentId(handoverId)) {
      throw problem(
        422,
        "Request validation failed",
        "handover_id must be a valid UUID.",
        "REQUEST_VALIDATION_FAILED",
        "request-validation-failed",
      );
    }
    return jsonResponse(await getHandoverById(env, context, handoverId), requestId);
  }

  if (path === `${API_PREFIX}/audit-events`) {
    if (request.method !== "GET") methodNotAllowed();
    return jsonResponse(await listAuditEvents(env, context, url), requestId);
  }

  if (path === `${API_PREFIX}/incidents/query`) {
    if (request.method !== "GET") methodNotAllowed();
    return jsonResponse(await listIncidents(env, context, url), requestId);
  }

  if (path === `${API_PREFIX}/incidents`) {
    if (request.method === "GET") {
      return jsonResponse(await listSimpleIncidents(env, context), requestId);
    }
    if (request.method === "POST") {
      return jsonResponse(
        await createIncident(env, context, request, requestId),
        requestId,
        201,
      );
    }
    methodNotAllowed();
  }

  const timelineMatch = path.match(
    /^\/api\/v1\/incidents\/([^/]+)\/timeline$/,
  );
  if (timelineMatch) {
    if (request.method !== "GET") methodNotAllowed();
    const incidentId = timelineMatch[1];
    if (!validIncidentId(incidentId)) {
      throw problem(
        422,
        "Request validation failed",
        "incident_id must be a valid UUID.",
        "REQUEST_VALIDATION_FAILED",
        "request-validation-failed",
      );
    }
    return jsonResponse(await listTimeline(env, context, incidentId), requestId);
  }

  const updateMatch = path.match(/^\/api\/v1\/incidents\/([^/]+)\/updates$/);
  if (updateMatch) {
    if (request.method !== "POST") methodNotAllowed();
    const incidentId = updateMatch[1];
    if (!validIncidentId(incidentId)) {
      throw problem(
        422,
        "Request validation failed",
        "incident_id must be a valid UUID.",
        "REQUEST_VALIDATION_FAILED",
        "request-validation-failed",
      );
    }
    return jsonResponse(
      await addIncidentUpdate(env, context, incidentId, request, requestId),
      requestId,
    );
  }

  const normalizeMatch = path.match(
    /^\/api\/v1\/incidents\/([^/]+)\/normalize$/,
  );
  if (normalizeMatch) {
    if (request.method !== "POST") methodNotAllowed();
    const incidentId = normalizeMatch[1];
    if (!validIncidentId(incidentId)) {
      throw problem(
        422,
        "Request validation failed",
        "incident_id must be a valid UUID.",
        "REQUEST_VALIDATION_FAILED",
        "request-validation-failed",
      );
    }
    return jsonResponse(
      await normalizeIncident(env, context, incidentId, request, requestId),
      requestId,
    );
  }

  const detailMatch = path.match(/^\/api\/v1\/incidents\/([^/]+)$/);
  if (detailMatch) {
    if (request.method !== "GET") methodNotAllowed();
    const incidentId = detailMatch[1];
    if (!validIncidentId(incidentId)) {
      throw problem(
        422,
        "Request validation failed",
        "incident_id must be a valid UUID.",
        "REQUEST_VALIDATION_FAILED",
        "request-validation-failed",
      );
    }
    return jsonResponse(await getIncident(env, context, incidentId), requestId);
  }

  throw problem(
    404,
    "Resource not found",
    "The requested API resource does not exist.",
    "RESOURCE_NOT_FOUND",
    "resource-not-found",
  );
}

export default {
  async fetch(request, env) {
    if (!new URL(request.url).pathname.startsWith(API_PREFIX)) {
      return env.ASSETS.fetch(request);
    }

    const requestId = resolveRequestId(request.headers.get("x-request-id"));
    const started = Date.now();
    let response;
    try {
      response = await routeApi(request, env, requestId);
    } catch (error) {
      if (error instanceof ApiProblem) {
        response = problemResponse(error, requestId);
      } else {
        console.error(JSON.stringify({
          event: "cloudflare_private_demo_unhandled",
          request_id: requestId,
          message: error instanceof Error ? error.message : String(error),
        }));
        response = problemResponse(
          problem(
            500,
            "Internal server error",
            "The private demo could not complete the request.",
            "INTERNAL_SERVER_ERROR",
            "internal-server-error",
          ),
          requestId,
        );
      }
    }
    console.log(JSON.stringify({
      event: "http_request",
      request_id: requestId,
      method: request.method,
      path: new URL(request.url).pathname,
      status_code: response.status,
      duration_ms: Date.now() - started,
    }));
    return response;
  },
};
