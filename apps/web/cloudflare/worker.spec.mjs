import { describe, expect, it } from "vitest";

import {
  ApiProblem,
  calculateShiftWindow,
  parseHandoverListQuery,
  parseIncidentListQuery,
  permissionsForRole,
  validateHandoverFinalize,
  validateIncidentCreate,
  validateIncidentNormalize,
  validateIncidentUpdate,
} from "./worker.mjs";

describe("Cloudflare private demo contract helpers", () => {
  it("normalizes a valid incident create payload", () => {
    const result = validateIncidentCreate(
      {
        title: "  Link indisponível  ",
        affected_resource: " Loja 001 ",
        severity: "HIGH",
        impact_type: "OUTAGE",
        symptoms: " Sem conectividade com a operadora. ",
        started_at: "2026-09-21T12:00:00Z",
      },
      new Date("2026-09-21T13:00:00Z"),
    );

    expect(result).toEqual({
      title: "Link indisponível",
      affected_resource: "Loja 001",
      severity: "HIGH",
      impact_type: "OUTAGE",
      symptoms: "Sem conectividade com a operadora.",
      started_at: "2026-09-21T12:00:00.000Z",
    });
  });

  it("rejects future incident start time", () => {
    expect(() =>
      validateIncidentCreate(
        {
          title: "Link indisponível",
          affected_resource: "Loja 001",
          severity: "HIGH",
          impact_type: "OUTAGE",
          symptoms: "Sem conectividade com a operadora.",
          started_at: "2026-09-21T14:00:00Z",
        },
        new Date("2026-09-21T13:00:00Z"),
      ),
    ).toThrowError(
      expect.objectContaining({
        code: "INCIDENT_STARTED_AT_IN_FUTURE",
        status: 422,
      }),
    );
  });

  it("forbids unexpected payload fields", () => {
    expect(() =>
      validateIncidentUpdate({ message: "Operadora acionada.", tenant_id: "x" }),
    ).toThrowError(
      expect.objectContaining({
        code: "REQUEST_VALIDATION_FAILED",
        status: 422,
      }),
    );
  });

  it("accepts optional normalize note", () => {
    expect(validateIncidentNormalize({})).toEqual({ note: null });
    expect(validateIncidentNormalize({ note: " Serviço restabelecido. " })).toEqual({
      note: "Serviço restabelecido.",
    });
  });

  it("parses pagination, filters and ordering", () => {
    const url = new URL(
      "https://demo.invalid/api/v1/incidents/query?status=OPEN&severity=HIGH&page=2&page_size=10&sort=updated_at&order=asc",
    );
    expect(parseIncidentListQuery(url)).toEqual({
      status: "OPEN",
      severity: "HIGH",
      started_from: null,
      started_to: null,
      page: 2,
      page_size: 10,
      sort: "updated_at",
      order: "asc",
    });
  });

  it("rejects an inverted period", () => {
    const url = new URL(
      "https://demo.invalid/api/v1/incidents/query?started_from=2026-09-22T00:00:00Z&started_to=2026-09-21T00:00:00Z",
    );
    expect(() => parseIncidentListQuery(url)).toThrowError(
      expect.objectContaining({
        code: "INCIDENT_INVALID_PERIOD",
        status: 422,
      }),
    );
  });

  it("keeps RBAC parity with the canonical backend", () => {
    expect(permissionsForRole("Viewer")).toEqual([
      "incident:read",
      "handover:read",
    ]);
    expect(permissionsForRole("Operator")).toEqual([
      "incident:read",
      "incident:create",
      "incident:update",
      "incident:normalize",
      "handover:read",
      "handover:finalize",
    ]);
    expect(permissionsForRole("Admin")).toHaveLength(6);
    expect(permissionsForRole("Unknown")).toEqual([]);
  });

  it("validates handover observations and rejects forged authority", () => {
    expect(validateHandoverFinalize({ observations: "  Plantão estável.  " })).toEqual({
      observations: "Plantão estável.",
    });
    expect(validateHandoverFinalize({ observations: "" })).toEqual({
      observations: null,
    });
    expect(() =>
      validateHandoverFinalize({
        observations: "Plantão estável.",
        tenant_id: "forged",
      }),
    ).toThrowError(
      expect.objectContaining({
        code: "REQUEST_VALIDATION_FAILED",
        status: 422,
      }),
    );
  });

  it("parses handover history pagination", () => {
    const url = new URL(
      "https://demo.invalid/api/v1/handovers?page=2&page_size=10",
    );
    expect(parseHandoverListQuery(url)).toEqual({ page: 2, page_size: 10 });
  });

  it("calculates the current shift window in UTC", () => {
    expect(
      calculateShiftWindow({
        timezone: "UTC",
        shift_start_local: "06:00:00",
        shift_duration_minutes: 720,
        now: new Date("2026-09-21T15:00:00Z"),
      }),
    ).toEqual({
      window_start: "2026-09-21T06:00:00.000Z",
      window_end: "2026-09-21T18:00:00.000Z",
    });
  });

  it("calculates a shift window with an IANA timezone", () => {
    expect(
      calculateShiftWindow({
        timezone: "America/Sao_Paulo",
        shift_start_local: "06:00:00",
        shift_duration_minutes: 720,
        now: new Date("2026-09-21T15:00:00Z"),
      }),
    ).toEqual({
      window_start: "2026-09-21T09:00:00.000Z",
      window_end: "2026-09-21T21:00:00.000Z",
    });
  });

  it("exposes typed API validation failures", () => {
    try {
      validateIncidentUpdate({ message: "x" });
      throw new Error("expected validation failure");
    } catch (error) {
      expect(error).toBeInstanceOf(ApiProblem);
      expect(error).toMatchObject({
        status: 422,
        code: "REQUEST_VALIDATION_FAILED",
      });
    }
  });
});
