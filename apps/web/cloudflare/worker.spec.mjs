import { describe, expect, it } from "vitest";

import {
  ApiProblem,
  parseIncidentListQuery,
  permissionsForRole,
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
    expect(permissionsForRole("Viewer")).toEqual(["incident:read"]);
    expect(permissionsForRole("Operator")).toEqual([
      "incident:read",
      "incident:create",
      "incident:update",
      "incident:normalize",
    ]);
    expect(permissionsForRole("Admin")).toHaveLength(4);
    expect(permissionsForRole("Unknown")).toEqual([]);
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
