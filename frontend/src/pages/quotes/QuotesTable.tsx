import { SavedQuoteSummary } from "@/api/types";

function formatHours(n: number): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(n);
}

type Props = {
  rows: SavedQuoteSummary[];
  selected: Set<string>;
  onToggle: (id: string) => void;
  onRowAction: (id: string, action: "duplicate" | "delete" | "pdf" | "open") => void;
};

export function QuotesTable({ rows, selected, onToggle, onRowAction }: Props) {
  return (
    <div className="card overflow-hidden">
      <table className="w-full text-sm">
        <thead className="border-b border-border">
          <tr className="text-left text-xs uppercase tracking-wide text-muted">
            <th className="px-3 py-2 w-8" />
            <th className="px-3 py-2">Name</th>
            <th className="px-3 py-2">Project</th>
            <th className="px-3 py-2">Industry</th>
            <th className="px-3 py-2 text-right">Hours</th>
            <th className="px-3 py-2">Range</th>
            <th className="px-3 py-2">Saved</th>
            <th className="px-3 py-2" />
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-b last:border-0 border-border hover:bg-steel-100/60">
              <td className="px-3 py-2">
                <input
                  type="checkbox"
                  checked={selected.has(r.id)}
                  onChange={() => onToggle(r.id)}
                  aria-label={`Select ${r.name}`}
                />
              </td>
              <td className="px-3 py-2 font-medium text-ink">
                <button onClick={() => onRowAction(r.id, "open")} className="hover:underline">
                  {r.name}
                </button>
              </td>
              <td className="px-3 py-2 text-muted">{r.project_name}</td>
              <td className="px-3 py-2 text-muted">{r.industry_segment}</td>
              <td className="px-3 py-2 text-right numeric tabular-nums text-ink">
                {formatHours(r.hours)}
              </td>
              <td className="px-3 py-2 text-muted numeric tabular-nums">
                {formatHours(r.range_low)}–{formatHours(r.range_high)}
              </td>
              <td className="px-3 py-2 text-muted">{new Date(r.created_at).toLocaleDateString()}</td>
              <td className="px-3 py-2 text-right">
                <div className="inline-flex gap-2 text-xs">
                  <button
                    className="text-brand hover:underline"
                    onClick={() => onRowAction(r.id, "duplicate")}
                  >
                    Duplicate
                  </button>
                  <button
                    className="text-brand hover:underline"
                    onClick={() => onRowAction(r.id, "pdf")}
                  >
                    PDF
                  </button>
                  <button
                    className="text-danger hover:underline"
                    onClick={() => onRowAction(r.id, "delete")}
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td colSpan={8} className="px-3 py-6 text-center text-muted">
                No saved quotes yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
