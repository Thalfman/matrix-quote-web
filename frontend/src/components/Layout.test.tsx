import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, afterEach } from "vitest";

import { renderWithProviders } from "@/test/render";
import { Layout } from "./Layout";

vi.mock("@/api/client", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
  getAdminToken: () => null,
  setAdminToken: vi.fn(),
  clearAdminToken: vi.fn(),
}));

import { api } from "@/api/client";

const mockGet = vi.mocked(api.get);

describe("Layout — INSIGHTS nav group", () => {
  afterEach(() => {
    mockGet.mockReset();
  });

  it("contains both 'Estimate Accuracy' and 'Executive Overview' links", async () => {
    mockGet.mockImplementation(async (url: string) => {
      if (url === "/health") return { data: { status: "ok", models_ready: true } };
      throw new Error(`Unexpected GET ${url}`);
    });

    renderWithProviders(<Layout />);

    await waitFor(() =>
      expect(screen.getByRole("link", { name: /estimate accuracy/i })).toBeInTheDocument(),
    );
    expect(screen.getByRole("link", { name: /executive overview/i })).toBeInTheDocument();

    const accuracyLink = screen.getByRole("link", { name: /estimate accuracy/i });
    const overviewLink = screen.getByRole("link", { name: /executive overview/i });
    expect(accuracyLink).toHaveAttribute("href", "/performance");
    expect(overviewLink).toHaveAttribute("href", "/insights");
  });
});
