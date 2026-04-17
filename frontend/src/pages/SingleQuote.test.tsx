import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test/render";

import { SingleQuote } from "./SingleQuote";

vi.mock("@/api/client", () => {
  return {
    api: {
      get: vi.fn(),
      post: vi.fn(),
    },
    getAdminToken: () => null,
    setAdminToken: vi.fn(),
    clearAdminToken: vi.fn(),
  };
});

import { api } from "@/api/client";

const mockGet = vi.mocked(api.get);
const mockPost = vi.mocked(api.post);

describe("SingleQuote", () => {
  afterEach(() => {
    mockGet.mockReset();
    mockPost.mockReset();
  });

  it("renders the not-trained empty state when /api/health reports models_ready=false", async () => {
    mockGet.mockImplementation(async (url: string) => {
      if (url === "/health") return { data: { status: "ok", models_ready: false } };
      if (url === "/catalog/dropdowns") {
        return {
          data: {
            industry_segment: [],
            system_category: [],
            automation_level: [],
            plc_family: [],
            hmi_family: [],
            vision_type: [],
          },
        };
      }
      throw new Error(`Unexpected GET ${url}`);
    });

    renderWithProviders(<SingleQuote />);

    expect(await screen.findByText(/models are not trained/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /estimate hours/i })).not.toBeInTheDocument();
  });

  it("renders the form when models are ready and submits a prediction", async () => {
    mockGet.mockImplementation(async (url: string) => {
      if (url === "/health") return { data: { status: "ok", models_ready: true } };
      if (url === "/catalog/dropdowns") {
        return {
          data: {
            industry_segment: ["Automotive"],
            system_category: ["Machine Tending"],
            automation_level: ["Robotic"],
            plc_family: ["AB Compact Logix"],
            hmi_family: ["AB PanelView Plus"],
            vision_type: ["None"],
          },
        };
      }
      throw new Error(`Unexpected GET ${url}`);
    });

    mockPost.mockResolvedValue({
      data: {
        ops: {
          me10: { p50: 12, p10: 10, p90: 14, std: 1.5, rel_width: 0.3, confidence: "high" },
        },
        total_p50: 100,
        total_p10: 80,
        total_p90: 120,
        sales_buckets: {
          ME: { p50: 12, p10: 10, p90: 14, rel_width: 0.3, confidence: "high" },
          EE: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
          PM: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
          Docs: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
          Build: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
          Robot: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
          Controls: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
          Install: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
          Travel: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
        },
      },
    });

    const { container } = renderWithProviders(<SingleQuote />);

    const button = await screen.findByRole("button", { name: /estimate hours/i });
    expect(button).toBeInTheDocument();

    const form = container.querySelector("form") as HTMLFormElement;
    expect(form).toBeInTheDocument();
    form.requestSubmit();

    await waitFor(() => expect(mockPost).toHaveBeenCalledTimes(1));
    const [url, payload] = mockPost.mock.calls[0];
    expect(url).toBe("/quote/single");
    expect(payload).toMatchObject({
      industry_segment: "Automotive",
      system_category: "Machine Tending",
      automation_level: "Robotic",
      has_controls: 1,
      has_robotics: 1,
      duplicate: 0,
      Retrofit: 0,
      log_quoted_materials_cost: 0,
    });

    expect(await screen.findByText(/recommended total · p50/i)).toBeInTheDocument();
  });

  const readyGetMock = async (url: string) => {
    if (url === "/health") return { data: { status: "ok", models_ready: true } };
    if (url === "/catalog/dropdowns") {
      return {
        data: {
          industry_segment: ["Automotive"],
          system_category: ["Machine Tending"],
          automation_level: ["Robotic"],
          plc_family: ["AB Compact Logix"],
          hmi_family: ["AB PanelView Plus"],
          vision_type: ["None"],
        },
      };
    }
    throw new Error(`Unexpected GET ${url}`);
  };

  const explainedResponse = {
    prediction: {
      ops: {
        me10: { p50: 12, p10: 10, p90: 14, std: 1.5, rel_width: 0.3, confidence: "high" },
      },
      total_p50: 100,
      total_p10: 80,
      total_p90: 120,
      sales_buckets: {
        ME: { p50: 12, p10: 10, p90: 14, rel_width: 0.3, confidence: "high" },
        EE: { p50: 0, p10: 0, p90: 0, rel_width: 0, confidence: "low" },
      },
    },
    drivers: [
      {
        operation: "me10",
        available: true,
        drivers: [
          { feature: "stations_count", contribution: 20, value: "4" },
          { feature: "robot_count", contribution: -5, value: "2" },
        ],
      },
    ],
    neighbors: [
      {
        project_name: "Alpha Project",
        year: 2023,
        industry_segment: "Automotive",
        automation_level: "Robotic",
        stations: 4,
        actual_hours: 110,
        similarity: 0.92,
      },
    ],
  };

  it("renders the skeleton while a quote is in-flight", async () => {
    mockGet.mockImplementation(readyGetMock);
    // Never-resolving post to hold the pending state.
    mockPost.mockImplementation(() => new Promise(() => {}));

    const { container } = renderWithProviders(<SingleQuote />);

    await screen.findByRole("button", { name: /estimate hours/i });
    const form = container.querySelector("form") as HTMLFormElement;
    form.requestSubmit();

    await waitFor(() => {
      expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
    });
  });

  it("switches between Estimate, Drivers, and Similar tabs once a result arrives", async () => {
    mockGet.mockImplementation(readyGetMock);
    mockPost.mockResolvedValue({ data: explainedResponse });

    const { container } = renderWithProviders(<SingleQuote />);

    await screen.findByRole("button", { name: /estimate hours/i });
    const form = container.querySelector("form") as HTMLFormElement;
    form.requestSubmit();

    // Wait for result panel to appear (hero heading visible).
    await screen.findByText(/ESTIMATED HOURS/i);

    // Estimate tab is active by default — bucket key visible.
    expect(screen.getByRole("tabpanel")).toBeInTheDocument();

    // Switch to Drivers tab.
    fireEvent.click(screen.getByRole("tab", { name: /^Drivers$/i }));
    await screen.findByText(/stations_count/i);

    // Switch to Similar tab.
    fireEvent.click(screen.getByRole("tab", { name: /^Similar$/i }));
    await screen.findByText(/Alpha Project/i);

    // Switch to Scenarios tab.
    fireEvent.click(screen.getByRole("tab", { name: /^Scenarios$/i }));
    await screen.findByText(/No scenarios saved/i);
  });

  it("keeps the hero number frozen at target under prefers-reduced-motion", async () => {
    window.matchMedia = (q: string) =>
      ({
        matches: q.includes("reduce"),
        addEventListener: () => {},
        removeEventListener: () => {},
      }) as unknown as MediaQueryList;

    mockGet.mockImplementation(readyGetMock);
    mockPost.mockResolvedValue({ data: explainedResponse });

    const { container } = renderWithProviders(<SingleQuote />);

    await screen.findByRole("button", { name: /estimate hours/i });
    const form = container.querySelector("form") as HTMLFormElement;
    form.requestSubmit();

    // Wait for result to appear.
    await screen.findByText(/ESTIMATED HOURS/i);

    // Hero should show the full target number (100) immediately, not 0.
    await waitFor(() => {
      const heroEl = container.querySelector(".text-display");
      expect(heroEl?.textContent).toBe("100");
    });
  });
});
