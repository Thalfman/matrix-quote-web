import { InsightsOverview } from "@/api/types";

function Card({ label, value, suffix }: { label: string; value: string; suffix?: string }) {
  return (
    <div className="card p-4">
      <div className="text-[10px] tracking-widest text-muted font-semibold uppercase">{label}</div>
      <div className="mt-1 text-2xl font-semibold numeric tabular-nums text-ink">
        {value}{suffix ? <span className="text-sm text-muted ml-1">{suffix}</span> : null}
      </div>
    </div>
  );
}

export function KpiCards({ data }: { data: InsightsOverview | undefined }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <Card label="Active quotes (30d)" value={(data?.active_quotes_30d ?? 0).toString()} />
      <Card label="Models trained" value={`${data?.models_trained ?? 0}/${data?.models_target ?? 12}`} />
      <Card label="Overall MAPE" value={data?.overall_mape != null ? data.overall_mape.toFixed(1) : "—"} suffix={data?.overall_mape != null ? "%" : ""} />
      <Card label="Confidence calibration" value={data?.calibration_within_band_pct != null ? data.calibration_within_band_pct.toFixed(1) : "—"} suffix={data?.calibration_within_band_pct != null ? "%" : ""} />
    </div>
  );
}
