import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MetricRow } from "@/api/types";

export function MapeByOperation({ rows }: { rows: MetricRow[] }) {
  // Prefer mape if present in metrics_summary.csv, else degrade to mae bars.
  const anyMape = rows.some((r) => "mape" in r && (r as unknown as { mape?: number }).mape != null);
  const data = rows.map((r) => ({
    op: r.target.replace(/_hours$/, ""),
    mape: anyMape ? (r as unknown as { mape?: number }).mape ?? 0 : (r.mae ?? 0),
  })).sort((a, b) => b.mape - a.mape);

  if (data.length === 0) {
    return (
      <div className="card p-6 text-sm text-muted">
        No training metrics yet. Once the models are trained, per-operation accuracy appears here.
      </div>
    );
  }

  return (
    <div className="card p-4 h-72">
      <div className="text-xs tracking-widest text-muted uppercase mb-2">
        {anyMape ? "MAPE by operation (%)" : "MAE by operation (hours)"}
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="op" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="mape" fill="#2563EB" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
