import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test/render";

import { QuotesActivityChart } from "./QuotesActivityChart";

vi.mock("recharts", async () => {
  const actual = await vi.importActual<typeof import("recharts")>("recharts");
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div>{children}</div>
    ),
  };
});

describe("QuotesActivityChart", () => {
  it("renders the section heading with empty rows", () => {
    renderWithProviders(<QuotesActivityChart rows={[]} />);
    expect(screen.getByText(/quotes per week/i)).toBeInTheDocument();
  });

  it("renders the section heading with populated rows", () => {
    const rows: [string, number][] = [
      ["2026-W10", 3],
      ["2026-W11", 5],
      ["2026-W12", 0],
    ];
    renderWithProviders(<QuotesActivityChart rows={rows} />);
    expect(screen.getByText(/quotes per week/i)).toBeInTheDocument();
  });
});
