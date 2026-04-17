import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { SavedQuote } from "@/api/types";

const BAR_COLORS = ["#2563EB", "#0F766E", "#B45309"];

export function CompareBucketsChart({ quotes }: { quotes: SavedQuote[] }) {
  const allBuckets = new Set<string>();
  quotes.forEach((q) =>
    Object.keys(q.prediction.sales_buckets ?? {}).forEach((k) => allBuckets.add(k)),
  );

  const data = Array.from(allBuckets).map((bucket) => {
    const row: Record<string, number | string> = { bucket };
    quotes.forEach((q, i) => {
      row[q.name || `Q${i + 1}`] = q.prediction.sales_buckets?.[bucket]?.p50 ?? 0;
    });
    return row;
  });

  return (
    <div className="card p-4 h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="bucket" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {quotes.map((q, i) => (
            <Bar
              key={q.id}
              dataKey={q.name || `Q${i + 1}`}
              fill={BAR_COLORS[i % BAR_COLORS.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
