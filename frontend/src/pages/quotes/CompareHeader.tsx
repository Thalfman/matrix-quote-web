import { SavedQuote } from "@/api/types";

function fmt(n: number) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(n);
}

export function CompareHeader({ quotes }: { quotes: SavedQuote[] }) {
  const base = quotes[0];
  return (
    <div
      className="grid gap-4"
      style={{ gridTemplateColumns: `160px repeat(${quotes.length}, minmax(0, 1fr))` }}
    >
      <div />
      {quotes.map((q) => (
        <div key={q.id} className="text-sm">
          <div className="font-semibold text-ink truncate">{q.name}</div>
          <div className="text-muted">{q.project_name}</div>
        </div>
      ))}

      <div className="text-xs tracking-widest text-muted uppercase">Hours</div>
      {quotes.map((q) => (
        <div key={q.id} className="text-xl font-semibold numeric tabular-nums text-ink">
          {fmt(q.prediction.total_p50)}
        </div>
      ))}

      <div className="text-xs tracking-widest text-muted uppercase">Range</div>
      {quotes.map((q) => (
        <div key={q.id} className="text-sm text-muted numeric tabular-nums">
          {fmt(q.prediction.total_p10)}–{fmt(q.prediction.total_p90)}
        </div>
      ))}

      <div className="text-xs tracking-widest text-muted uppercase">
        &#916; vs {base.name}
      </div>
      {quotes.map((q, i) => {
        const d = q.prediction.total_p50 - base.prediction.total_p50;
        const pct =
          base.prediction.total_p50 > 0 ? (d / base.prediction.total_p50) * 100 : 0;
        return (
          <div key={q.id} className="text-sm numeric tabular-nums">
            {i === 0
              ? "—"
              : `${d >= 0 ? "+" : ""}${fmt(d)} (${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%)`}
          </div>
        );
      })}
    </div>
  );
}
