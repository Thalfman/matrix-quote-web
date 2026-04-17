import { screen, waitFor } from "@testing-library/react";
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
});
