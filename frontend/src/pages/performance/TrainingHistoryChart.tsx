import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TrainingRunRow } from "@/api/types";

export function TrainingHistoryChart({ rows }: { rows: TrainingRunRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="card p-6 text-sm text-muted">
        Training history isn't persisted yet. Once each training run writes a snapshot, this chart shows MAPE over time.
      </div>
    );
  }
  const data = rows.map((r) => ({
    date: new Date(r.trained_at).toLocaleDateString(),
    mape: r.overall_mape,
    rows: r.rows,
  }));
  return (
    <div className="card p-4 h-72">
      <div className="text-xs tracking-widest text-muted uppercase mb-2">Training history</div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Line dataKey="mape" stroke="#2563EB" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
