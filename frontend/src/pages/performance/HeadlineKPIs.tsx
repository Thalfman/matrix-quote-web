import { PerformanceHeadline } from "@/api/types";

function KPI({ label, value, suffix }: { label: string; value: number | null; suffix?: string }) {
  const txt = value == null ? "—" : `${value.toFixed(1)}${suffix ?? ""}`;
  return (
    <div className="card p-4">
      <div className="text-[10px] tracking-widest text-muted font-semibold uppercase">{label}</div>
      <div className="mt-1 text-2xl font-semibold numeric tabular-nums text-ink">{txt}</div>
    </div>
  );
}

export function HeadlineKPIs({ head }: { head: PerformanceHeadline | undefined }) {
  return (
    <div className="grid gap-3 sm:grid-cols-3">
      <KPI label="Overall MAPE" value={head?.overall_mape ?? null} suffix="%" />
      <KPI label="Within ±10%"  value={head?.within_10_pct ?? null} suffix="%" />
      <KPI label="Within ±20%"  value={head?.within_20_pct ?? null} suffix="%" />
    </div>
  );
}
