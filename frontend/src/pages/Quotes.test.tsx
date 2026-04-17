import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test/render";

import { Quotes } from "./Quotes";

vi.mock("@/api/client", () => {
  return {
    api: {
      get: vi.fn(),
      post: vi.fn(),
      delete: vi.fn(),
    },
    getAdminToken: () => null,
    setAdminToken: vi.fn(),
    clearAdminToken: vi.fn(),
  };
});

import { api } from "@/api/client";

const mockGet = vi.mocked(api.get);

const rows = [
  {
    id: "a",
    name: "Option A",
    project_name: "Line 3",
    client_name: null,
    industry_segment: "Automotive",
    hours: 1200,
    range_low: 1000,
    range_high: 1400,
    created_at: "2026-04-01T00:00:00Z",
    created_by: "Tester",
  },
  {
    id: "b",
    name: "Option B",
    project_name: "Line 3",
    client_name: null,
    industry_segment: "Automotive",
    hours: 980,
    range_low: 800,
    range_high: 1150,
    created_at: "2026-04-02T00:00:00Z",
    created_by: "Tester",
  },
];

describe("Quotes", () => {
  it("lists saved quotes from /quotes mock", async () => {
    mockGet.mockImplementation(async (url: string) => {
      if (url === "/quotes") return { data: { total: rows.length, rows } };
      throw new Error(`Unexpected GET ${url}`);
    });

    renderWithProviders(<Quotes />);

    await waitFor(() => expect(screen.getByText("Option A")).toBeInTheDocument());
    expect(screen.getByText("Option B")).toBeInTheDocument();
  });

  it("Compare button starts disabled, stays disabled with 1 checkbox, enables with 2", async () => {
    mockGet.mockImplementation(async (url: string) => {
      if (url === "/quotes") return { data: { total: rows.length, rows } };
      throw new Error(`Unexpected GET ${url}`);
    });

    renderWithProviders(<Quotes />);

    await screen.findByText("Option A");

    const compareBtn = screen.getByRole("button", { name: /Compare/i });
    expect(compareBtn).toBeDisabled();

    const checkboxes = screen.getAllByRole("checkbox");
    fireEvent.click(checkboxes[0]);
    expect(compareBtn).toBeDisabled();

    fireEvent.click(checkboxes[1]);
    expect(compareBtn).not.toBeDisabled();
  });
});
