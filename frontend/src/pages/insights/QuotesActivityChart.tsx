import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function QuotesActivityChart({ rows }: { rows: [string, number][] }) {
  const data = rows.map(([week, count]) => ({ week, count }));
  return (
    <div className="card p-4 h-64">
      <div className="text-xs tracking-widest text-muted uppercase mb-2">Quotes per week (last 26)</div>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" tick={{ fontSize: 10 }} />
          <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" fill="#2563EB" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
