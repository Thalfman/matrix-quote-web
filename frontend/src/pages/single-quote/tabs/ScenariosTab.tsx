// frontend/src/pages/single-quote/tabs/ScenariosTab.tsx
import { Scenario } from "../Scenario";

function formatHours(n: number): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(n);
}

export function ScenariosTab({
  scenarios,
  onRemove,
  onCompare,
}: {
  scenarios: Scenario[];
  onRemove: (id: string) => void;
  onCompare: () => void;
}) {
  if (scenarios.length === 0) {
    return (
      <div className="text-sm text-muted">
        No scenarios saved yet this session. Click <span className="text-ink font-medium">Save scenario</span> to start building a comparison.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {scenarios.map((s) => (
        <div key={s.id} className="card p-3 flex items-center gap-3">
          <div className="flex-1">
            <div className="font-medium text-ink truncate">{s.name}</div>
            <div className="text-xs text-muted">{new Date(s.createdAt).toLocaleString()}</div>
          </div>
          <div className="numeric tabular-nums text-ink">
            {formatHours(s.result.prediction.total_p50)} hrs
          </div>
          <button
            type="button"
            onClick={() => onRemove(s.id)}
            className="text-xs text-muted hover:text-danger transition-colors"
          >
            Remove
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={onCompare}
        disabled={scenarios.length < 2}
        className="text-sm text-brand disabled:text-muted disabled:cursor-not-allowed"
      >
        Compare {scenarios.length} scenario{scenarios.length === 1 ? "" : "s"}
        {scenarios.length < 2 && " (need at least 2)"}
      </button>
    </div>
  );
}
