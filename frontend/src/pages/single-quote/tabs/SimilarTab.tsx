// frontend/src/pages/single-quote/tabs/SimilarTab.tsx
import { NeighborProject } from "@/api/types";

function formatHours(n: number): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(n);
}

function similarityDots(sim: number): number {
  if (sim >= 0.90) return 5;
  if (sim >= 0.80) return 4;
  if (sim >= 0.65) return 3;
  if (sim >= 0.50) return 2;
  return 1;
}

export function SimilarTab({
  neighbors,
  estimate,
}: {
  neighbors: NeighborProject[] | null | undefined;
  estimate: number;
}) {
  if (!neighbors || neighbors.length === 0) {
    return (
      <div className="text-sm text-muted">
        No similar historical projects were found.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {neighbors.map((n, i) => {
        const delta = n.actual_hours - estimate;
        const deltaPct = estimate > 0 ? (delta / estimate) * 100 : 0;
        const dots = similarityDots(n.similarity);
        return (
          <div key={`${n.project_name}-${i}`} className="card p-4 space-y-1">
            <div className="flex items-center justify-between">
              <div className="font-medium text-ink truncate">{n.project_name}</div>
              <div className="flex items-center gap-1" aria-label={`Similarity ${Math.round(n.similarity * 100)}%`}>
                {[1,2,3,4,5].map((k) => (
                  <span key={k} className={"w-1.5 h-1.5 rounded-full " + (k <= dots ? "bg-brand" : "bg-steel-200")} />
                ))}
              </div>
            </div>
            <div className="text-sm text-muted">
              {n.industry_segment} · {n.automation_level}
              {n.stations != null && <> · {n.stations} stations</>}
              {n.year != null && <> · {n.year}</>}
            </div>
            <div className="text-sm">
              <span className="text-muted">Actual:</span>{" "}
              <span className="numeric tabular-nums text-ink">{formatHours(n.actual_hours)}</span>
              <span className="text-muted"> · today's estimate {formatHours(estimate)} · Δ </span>
              <span className="numeric tabular-nums text-ink">
                {delta >= 0 ? "+" : ""}{formatHours(delta)} ({deltaPct >= 0 ? "+" : ""}{deltaPct.toFixed(1)}%)
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
