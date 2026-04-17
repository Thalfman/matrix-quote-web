import { act, renderHook } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { useCountUp } from "./useCountUp";

describe("useCountUp", () => {
  it("animates from 0 to target when reduced motion is not set", () => {
    vi.useFakeTimers({ toFake: ["requestAnimationFrame", "performance"] });
    const { result } = renderHook(() => useCountUp(1000, { durationMs: 500 }));

    expect(result.current).toBe(0);
    act(() => { vi.advanceTimersByTime(500); });
    expect(Math.round(result.current)).toBe(1000);
    vi.useRealTimers();
  });

  it("returns the target immediately when prefers-reduced-motion", () => {
    const match = vi.fn().mockReturnValue({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() });
    window.matchMedia = match as typeof window.matchMedia;

    const { result } = renderHook(() => useCountUp(1000));
    expect(result.current).toBe(1000);
  });
});
