import { SavedQuote } from "@/api/types";

export function CompareInputDiff({ quotes }: { quotes: SavedQuote[] }) {
  const keys = new Set<string>();
  for (const q of quotes) Object.keys(q.inputs).forEach((k) => keys.add(k));

  const diffRows: { field: string; values: string[] }[] = [];
  for (const k of keys) {
    const values = quotes.map((q) => String((q.inputs as Record<string, unknown>)[k] ?? ""));
    if (new Set(values).size > 1) diffRows.push({ field: k, values });
  }

  if (diffRows.length === 0) {
    return (
      <div className="text-sm text-muted">These scenarios have identical inputs.</div>
    );
  }

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-left text-xs uppercase tracking-wide text-muted">
          <th className="px-3 py-2">Field</th>
          {quotes.map((q) => (
            <th key={q.id} className="px-3 py-2">
              {q.name}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {diffRows.map(({ field, values }) => (
          <tr key={field} className="border-b last:border-0 border-border">
            <td className="px-3 py-2 text-muted">{field}</td>
            {values.map((v, i) => (
              <td key={i} className="px-3 py-2 text-ink">
                {v || "—"}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
