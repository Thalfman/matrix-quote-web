import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderWithProviders } from "@/test/render";

import { AccuracyHeatmap } from "./AccuracyHeatmap";

describe("AccuracyHeatmap", () => {
  it("renders empty-state message when operations and quarters are empty", () => {
    renderWithProviders(
      <AccuracyHeatmap operations={[]} quarters={[]} matrix={[]} />,
    );
    expect(screen.getByText(/accuracy heatmap populates once/i)).toBeInTheDocument();
  });

  it("renders the table with operation rows and quarter columns when data is present", () => {
    const operations = ["welding", "machining"];
    const quarters = ["2025Q3", "2025Q4"];
    const matrix = [
      [12.5, 10.1],
      [null, 8.3],
    ];
    renderWithProviders(
      <AccuracyHeatmap operations={operations} quarters={quarters} matrix={matrix} />,
    );
    expect(screen.getByText("welding")).toBeInTheDocument();
    expect(screen.getByText("machining")).toBeInTheDocument();
    expect(screen.getByText("2025Q3")).toBeInTheDocument();
    expect(screen.getByText("2025Q4")).toBeInTheDocument();
  });

  it("renders 'no data' title attribute for null cells", () => {
    const operations = ["welding"];
    const quarters = ["2025Q3"];
    const matrix = [[null]];
    const { container } = renderWithProviders(
      <AccuracyHeatmap operations={operations} quarters={quarters} matrix={matrix} />,
    );
    const noDataCell = container.querySelector('[title="no data"]');
    expect(noDataCell).toBeInTheDocument();
  });

  it("renders formatted % title for non-null cells", () => {
    const operations = ["welding"];
    const quarters = ["2025Q3"];
    const matrix = [[15.75]];
    const { container } = renderWithProviders(
      <AccuracyHeatmap operations={operations} quarters={quarters} matrix={matrix} />,
    );
    const cell = container.querySelector('[title="15.8%"]');
    expect(cell).toBeInTheDocument();
  });
});
