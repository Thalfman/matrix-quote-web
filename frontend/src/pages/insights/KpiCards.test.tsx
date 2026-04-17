import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderWithProviders } from "@/test/render";

import { KpiCards } from "./KpiCards";

describe("KpiCards", () => {
  it("renders zero/dash values when data is undefined (loading state)", () => {
    renderWithProviders(<KpiCards data={undefined} />);
    expect(screen.getByText(/active quotes/i)).toBeInTheDocument();
    // Models trained shows separate value span and suffix "/ 12"
    // (active_quotes_30d also renders "0" so use getAllByText)
    expect(screen.getAllByText("0").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("/ 12")).toBeInTheDocument();
    // Overall MAPE and calibration show em-dashes
    const dashes = screen.getAllByText("—");
    expect(dashes.length).toBeGreaterThanOrEqual(2);
  });

  it("renders populated values from InsightsOverview data", () => {
    const data = {
      active_quotes_30d: 7,
      models_trained: 8,
      models_target: 12,
      overall_mape: 13.6,
      calibration_within_band_pct: 82.5,
      quotes_activity: [],
      latest_quotes: [],
      accuracy_heatmap: [],
      operations: [],
      quarters: [],
    };
    renderWithProviders(<KpiCards data={data} />);
    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("8")).toBeInTheDocument();
    expect(screen.getByText("/ 12")).toBeInTheDocument();
    expect(screen.getByText("13.6")).toBeInTheDocument();
    expect(screen.getByText("82.5")).toBeInTheDocument();
  });

  it("renders all four card labels", () => {
    renderWithProviders(<KpiCards data={undefined} />);
    expect(screen.getByText(/active quotes/i)).toBeInTheDocument();
    expect(screen.getByText(/models trained/i)).toBeInTheDocument();
    expect(screen.getByText(/overall mape/i)).toBeInTheDocument();
    expect(screen.getByText(/confidence calibration/i)).toBeInTheDocument();
  });
});
