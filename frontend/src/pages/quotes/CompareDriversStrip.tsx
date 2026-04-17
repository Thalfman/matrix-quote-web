import { SavedQuote } from "@/api/types";

export function CompareDriversStrip({ quotes }: { quotes: SavedQuote[] }) {
  return (
    <div
      className="grid gap-4"
      style={{ gridTemplateColumns: `repeat(${quotes.length}, minmax(0,1fr))` }}
    >
      {quotes.map((q) => (
        <div key={q.id} className="card p-4">
          <div className="text-xs tracking-widest text-muted uppercase">{q.name}</div>
          <div className="mt-2 text-sm text-muted">
            Top drivers were recorded at quote time and are not re-computed here.
          </div>
        </div>
      ))}
    </div>
  );
}
