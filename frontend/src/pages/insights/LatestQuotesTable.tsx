import { Link } from "react-router-dom";
import { SavedQuoteSummary } from "@/api/types";

function fmt(n: number) { return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(n); }

export function LatestQuotesTable({ rows }: { rows: SavedQuoteSummary[] }) {
  if (rows.length === 0) {
    return <div className="card p-6 text-sm text-muted">No saved quotes yet.</div>;
  }
  return (
    <div className="card overflow-hidden">
      <table className="w-full text-sm">
        <thead className="border-b border-border">
          <tr className="text-left text-xs uppercase tracking-wide text-muted">
            <th className="px-3 py-2">Name</th>
            <th className="px-3 py-2">Project</th>
            <th className="px-3 py-2 text-right">Hours</th>
            <th className="px-3 py-2">Saved</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-b last:border-0 border-border">
              <td className="px-3 py-2 text-ink">{r.name}</td>
              <td className="px-3 py-2 text-muted">{r.project_name}</td>
              <td className="px-3 py-2 text-right numeric tabular-nums text-ink">{fmt(r.hours)}</td>
              <td className="px-3 py-2 text-muted">{new Date(r.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="border-t border-border p-3 text-right">
        <Link to="/quotes" className="text-sm text-brand hover:underline">See all saved quotes →</Link>
      </div>
    </div>
  );
}
