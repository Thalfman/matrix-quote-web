// frontend/src/pages/single-quote/ResultSkeleton.tsx
export function ResultSkeleton() {
  return (
    <div className="animate-pulse space-y-4" aria-hidden="true">
      <div className="card p-6">
        <div className="h-3 w-32 bg-steel-200 rounded" />
        <div className="mt-4 h-14 w-40 bg-steel-200 rounded" />
        <div className="mt-3 h-3 w-60 bg-steel-200 rounded" />
      </div>
      <div className="card p-6 space-y-3">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="h-3 w-24 bg-steel-200 rounded" />
            <div className="flex-1 h-3 bg-steel-200 rounded" />
            <div className="h-3 w-10 bg-steel-200 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
