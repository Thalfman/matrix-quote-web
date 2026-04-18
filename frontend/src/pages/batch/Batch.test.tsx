import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { toast } from "sonner";

import { BATCH_SCHEMA, SAMPLE_RECENT_BATCHES } from "./fixtures";
import { BatchDropzone } from "./BatchDropzone";
import { BatchSchemaRef } from "./BatchSchemaRef";
import { BatchRecentList } from "./BatchRecentList";

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

// ─── BatchDropzone ────────────────────────────────────────────────────────────

describe("BatchDropzone", () => {
  it("clicking Select file then changing input emits Received toast with file name", () => {
    render(<BatchDropzone />);

    const selectBtn = screen.getByRole("button", { name: /Select file/i });
    // The button calls inputRef.current.click(); we can't fully test that in jsdom,
    // but we can directly fire a change event on the hidden input.
    const input = document.querySelector<HTMLInputElement>('input[type="file"]')!;
    expect(input).not.toBeNull();

    const file = new File(["data"], "x.csv", { type: "text/csv" });
    Object.defineProperty(input, "files", { value: [file], configurable: true });
    fireEvent.change(input);

    expect(vi.mocked(toast.info)).toHaveBeenCalledWith(
      expect.stringContaining("Received"),
    );
    expect(vi.mocked(toast.info)).toHaveBeenCalledWith(
      expect.stringContaining("x.csv"),
    );

    // Reset for isolation
    vi.mocked(toast.info).mockReset();

    // Verify "Select file" button is rendered (existence / click path check)
    expect(selectBtn).toBeInTheDocument();
  });

  it("drag-and-drop a file emits Received toast with file name", () => {
    render(<BatchDropzone />);

    const dropzone = screen
      .getByText(/Drop a CSV or XLSX/i)
      .closest("div[class]")!
      .parentElement!;

    const file = new File(["data"], "dropped.csv", { type: "text/csv" });

    // Build a minimal synthetic drag event with dataTransfer.files
    const dataTransfer = { files: [file] } as unknown as DataTransfer;

    fireEvent.dragOver(dropzone, { dataTransfer });
    fireEvent.drop(dropzone, { dataTransfer });

    expect(vi.mocked(toast.info)).toHaveBeenCalledWith(
      expect.stringContaining("Received"),
    );
    expect(vi.mocked(toast.info)).toHaveBeenCalledWith(
      expect.stringContaining("dropped.csv"),
    );

    vi.mocked(toast.info).mockReset();
  });

  it("clicking Download template emits a toast containing Template (distinct message)", () => {
    render(<BatchDropzone />);

    const templateBtn = screen.getByRole("button", { name: /Download template/i });
    fireEvent.click(templateBtn);

    expect(vi.mocked(toast.info)).toHaveBeenCalledWith(
      expect.stringContaining("Template"),
    );

    // Confirm it is NOT the upload message
    const calls = vi.mocked(toast.info).mock.calls.map((c) => c[0] as string);
    expect(calls.some((msg) => msg.includes("Received"))).toBe(false);

    vi.mocked(toast.info).mockReset();
  });
});

// ─── BatchSchemaRef ───────────────────────────────────────────────────────────

describe("BatchSchemaRef", () => {
  it("renders one row per BATCH_SCHEMA entry (22 rows)", () => {
    render(<BatchSchemaRef />);

    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(BATCH_SCHEMA.length);
    expect(BATCH_SCHEMA.length).toBe(22);
  });

  it("header shows '22 fields' and '6 required'", () => {
    render(<BatchSchemaRef />);

    const requiredCount = BATCH_SCHEMA.filter((r) => r.required).length;
    expect(requiredCount).toBe(6);

    expect(screen.getByText(`${BATCH_SCHEMA.length} fields · ${requiredCount} required`)).toBeInTheDocument();
  });

  it("required rows display 'Required' label and optional rows display 'Optional' label", () => {
    render(<BatchSchemaRef />);

    // There should be at least one Required and at least one Optional
    const requiredLabels = screen.getAllByText("Required");
    const optionalLabels = screen.getAllByText("Optional");

    expect(requiredLabels.length).toBeGreaterThan(0);
    expect(optionalLabels.length).toBeGreaterThan(0);

    // Exact counts match the fixture
    expect(requiredLabels).toHaveLength(BATCH_SCHEMA.filter((r) => r.required).length);
    expect(optionalLabels).toHaveLength(BATCH_SCHEMA.filter((r) => !r.required).length);
  });
});

// ─── BatchRecentList ──────────────────────────────────────────────────────────

describe("BatchRecentList", () => {
  it("renders a row for each entry in SAMPLE_RECENT_BATCHES (3 rows)", () => {
    render(<BatchRecentList />);

    for (const batch of SAMPLE_RECENT_BATCHES) {
      expect(screen.getByText(batch.fileName)).toBeInTheDocument();
    }
  });

  it("renders relative-time labels matching \\d+[dwm]\\s*ago or 'yesterday' patterns", () => {
    render(<BatchRecentList />);

    // The fixtures are 2d, 5d, 9d ago relative to Date.now(), so all match Xd ago
    const relativePattern = /(\d+[dwm]\s*ago|yesterday|today)/i;
    const container = document.body;
    const text = container.textContent ?? "";

    // Check at least one relative label is present
    expect(relativePattern.test(text)).toBe(true);

    // More granular: each fixture row should produce a relative label
    // The 3 batches are 2d, 5d, 9d ago — find these specifically
    expect(screen.getByText("2d ago")).toBeInTheDocument();
    expect(screen.getByText("5d ago")).toBeInTheDocument();
    expect(screen.getByText("9d ago")).toBeInTheDocument();
  });

  it("each row has an Open button", () => {
    render(<BatchRecentList />);

    const openButtons = screen.getAllByRole("button", { name: /^Open$/i });
    expect(openButtons).toHaveLength(SAMPLE_RECENT_BATCHES.length);
  });
});
