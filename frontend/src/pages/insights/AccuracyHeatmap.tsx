export function AccuracyHeatmap({
  operations, quarters, matrix,
}: {
  operations: string[];
  quarters: string[];
  matrix: (number | null)[][];
}) {
  if (operations.length === 0 || quarters.length === 0) {
    return (
      <div className="card p-6 text-sm text-muted">
        Accuracy heatmap populates once per-quarter training history is persisted.
      </div>
    );
  }

  const all = matrix.flat().filter((v): v is number => v != null);
  const max = all.length ? Math.max(...all) : 1;

  const color = (v: number | null): string => {
    if (v == null) return "#F6F8FB";
    const t = Math.min(1, v / Math.max(max, 1));
    // 0 = lightest, 1 = darkest brand
    const shades = ["#DBEAFE", "#BFDBFE", "#93C5FD", "#60A5FA", "#2563EB"];
    return shades[Math.min(shades.length - 1, Math.floor(t * shades.length))];
  };

  return (
    <div className="card p-4">
      <div className="text-xs tracking-widest text-muted uppercase mb-3">MAPE by op × quarter</div>
      <div className="overflow-x-auto">
        <table className="text-xs">
          <thead>
            <tr>
              <th />
              {quarters.map((q) => <th key={q} className="px-2 py-1 text-muted font-medium">{q}</th>)}
            </tr>
          </thead>
          <tbody>
            {operations.map((op, r) => (
              <tr key={op}>
                <td className="pr-3 py-1 text-right text-muted whitespace-nowrap">{op}</td>
                {matrix[r].map((v, c) => (
                  <td
                    key={c}
                    title={v == null ? "no data" : `${v.toFixed(1)}%`}
                    style={{ background: color(v) }}
                    className="w-12 h-7 border border-border"
                  />
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
