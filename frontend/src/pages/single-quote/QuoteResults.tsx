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

import { QuotePrediction } from "@/api/types";
import { ConfidenceDot } from "@/components/ConfidenceDot";
import { ResultHero } from "@/components/ResultHero";
import { Tabs } from "@/components/Tabs";
import { formatHours } from "@/lib/utils";

import { OPERATION_ORDER, SALES_BUCKETS, SalesBucket } from "./schema";

type Props = {
  prediction: QuotePrediction;
  quotedHoursByBucket: Partial<Record<SalesBucket, number>>;
};

export function QuoteResults({ prediction, quotedHoursByBucket }: Props) {
  const hasQuoted = Object.keys(quotedHoursByBucket).length > 0;
  const totalQuoted = Object.values(quotedHoursByBucket).reduce((s, v) => s + (v ?? 0), 0);
  const totalDelta = totalQuoted - prediction.total_p50;
  const statusLabel = hasQuoted
    ? Math.abs(totalDelta) <= Math.max(0.1 * Math.abs(prediction.total_p50), 10)
      ? "Aligned with model"
      : totalDelta > 0
        ? "Quote above model"
        : "Quote below model"
    : null;

  const meta = hasQuoted
    ? [
        { label: "Your quote", value: `${formatHours(totalQuoted)} h` },
        { label: "Delta", value: `${totalDelta >= 0 ? "+" : ""}${formatHours(totalDelta)} h` },
        ...(statusLabel ? [{ label: "Status", value: statusLabel }] : []),
      ]
    : undefined;

  return (
    <div className="mt-8">
      <ResultHero
        label="Recommended total · P50"
        value={formatHours(prediction.total_p50)}
        unit="hours"
        meta={meta}
      />

      <Tabs
        tabs={[
          {
            id: "sales",
            label: "Sales view",
            content: <SalesView prediction={prediction} quotedHoursByBucket={quotedHoursByBucket} />,
          },
          {
            id: "ops",
            label: "Operations view",
            content: <OperationsView prediction={prediction} />,
          },
        ]}
      />
    </div>
  );
}

function SalesView({ prediction, quotedHoursByBucket }: Props) {
  const hasQuoted = Object.keys(quotedHoursByBucket).length > 0;

  const rows = SALES_BUCKETS.map((bucket) => {
    const pred = prediction.sales_buckets[bucket];
    if (!pred) return null;
    const quoted = quotedHoursByBucket[bucket];
    const delta = quoted != null ? quoted - pred.p50 : null;
    const status =
      delta == null
        ? null
        : Math.abs(delta) <= Math.max(0.1 * Math.abs(pred.p50), 5)
          ? "Close"
          : delta > 0
            ? "Over"
            : "Under";
    return { bucket, pred, quoted, delta, status };
  }).filter((r): r is NonNullable<typeof r> => r !== null);

  return (
    <div className="space-y-6">
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left muted border-b border-border dark:border-border-dark">
              <th className="py-3 px-4 font-medium">Role</th>
              <th className="py-3 px-4 font-medium text-right">Recommended (P50)</th>
              <th className="py-3 px-4 font-medium text-right">Range (P10–P90)</th>
              <th className="py-3 px-4 font-medium">Confidence</th>
              {hasQuoted && (
                <>
                  <th className="py-3 px-4 font-medium text-right">Quoted</th>
                  <th className="py-3 px-4 font-medium text-right">Delta</th>
                  <th className="py-3 px-4 font-medium">Status</th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.bucket}
                className="border-b border-border/50 dark:border-border-dark/50 last:border-0"
              >
                <td className="py-2 px-4">{r.bucket}</td>
                <td className="py-2 px-4 text-right numeric">{formatHours(r.pred.p50)}</td>
                <td className="py-2 px-4 text-right numeric muted">
                  {formatHours(r.pred.p10)}–{formatHours(r.pred.p90)}
                </td>
                <td className="py-2 px-4">
                  <ConfidenceDot value={r.pred.confidence} />
                </td>
                {hasQuoted && (
                  <>
                    <td className="py-2 px-4 text-right numeric">
                      {r.quoted != null ? formatHours(r.quoted) : "—"}
                    </td>
                    <td className="py-2 px-4 text-right numeric">
                      {r.delta != null ? `${r.delta >= 0 ? "+" : ""}${formatHours(r.delta)}` : "—"}
                    </td>
                    <td className="py-2 px-4 text-xs muted">{r.status ?? "—"}</td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {hasQuoted && (
        <div className="card p-5">
          <div className="text-xs tracking-widest muted mb-3">MODEL VS YOUR QUOTE</div>
          <ComparisonChart rows={rows} />
        </div>
      )}
    </div>
  );
}

function ComparisonChart({
  rows,
}: {
  rows: { bucket: string; pred: { p50: number }; quoted: number | null | undefined }[];
}) {
  const data = rows.map((r) => ({
    bucket: r.bucket,
    Recommended: Number(r.pred.p50.toFixed(1)),
    Quoted: r.quoted != null ? Number(r.quoted.toFixed(1)) : 0,
  }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.3} />
        <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} label={{ value: "Hours", angle: -90, position: "insideLeft", offset: 10, fontSize: 11 }} />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="Recommended" fill="#2563EB" radius={[3, 3, 0, 0]} />
        <Bar dataKey="Quoted" fill="#60A5FA" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function OperationsView({ prediction }: { prediction: QuotePrediction }) {
  const orderedOps = OPERATION_ORDER.filter((op) => prediction.ops[op]);
  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left muted border-b border-border dark:border-border-dark">
            <th className="py-3 px-4 font-medium">Operation</th>
            <th className="py-3 px-4 font-medium text-right">P10</th>
            <th className="py-3 px-4 font-medium text-right">P50</th>
            <th className="py-3 px-4 font-medium text-right">P90</th>
            <th className="py-3 px-4 font-medium text-right">Std</th>
            <th className="py-3 px-4 font-medium text-right">Rel width</th>
            <th className="py-3 px-4 font-medium">Confidence</th>
          </tr>
        </thead>
        <tbody>
          {orderedOps.map((op) => {
            const p = prediction.ops[op];
            return (
              <tr
                key={op}
                className="border-b border-border/50 dark:border-border-dark/50 last:border-0"
              >
                <td className="py-2 px-4 font-mono text-xs">{op}</td>
                <td className="py-2 px-4 text-right numeric">{formatHours(p.p10)}</td>
                <td className="py-2 px-4 text-right numeric">{formatHours(p.p50)}</td>
                <td className="py-2 px-4 text-right numeric">{formatHours(p.p90)}</td>
                <td className="py-2 px-4 text-right numeric muted">{p.std.toFixed(2)}</td>
                <td className="py-2 px-4 text-right numeric muted">{p.rel_width.toFixed(2)}</td>
                <td className="py-2 px-4">
                  <ConfidenceDot value={p.confidence} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
