import { useSearchParams } from "react-router-dom";
import { useQueries } from "@tanstack/react-query";

import { api } from "@/api/client";
import { SavedQuote } from "@/api/types";
import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";

import { CompareBucketsChart } from "./quotes/CompareBucketsChart";
import { CompareDriversStrip } from "./quotes/CompareDriversStrip";
import { CompareHeader } from "./quotes/CompareHeader";
import { CompareInputDiff } from "./quotes/CompareInputDiff";

export function Compare() {
  const [params] = useSearchParams();
  const ids = (params.get("ids") ?? "").split(",").filter(Boolean);

  const queries = useQueries({
    queries: ids.map((id) => ({
      queryKey: ["savedQuote", id],
      queryFn: async () => (await api.get<SavedQuote>(`/quotes/${id}`)).data,
    })),
  });

  const loaded = queries.every((q) => q.data);
  const quotes = loaded ? queries.map((q) => q.data!) : [];

  if (ids.length < 2 || ids.length > 3) {
    return (
      <>
        <PageHeader eyebrow="Quotes" title="Compare" />
        <EmptyState
          title="Select 2-3 scenarios to compare"
          body="Open the Saved Quotes list and tick 2 or 3 rows before pressing Compare."
        />
      </>
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Quotes"
        title="Compare"
        description={`Comparing ${ids.length} scenarios.`}
      />
      {!loaded ? (
        <div className="mt-6 card p-6 text-sm text-muted">Loading scenarios...</div>
      ) : (
        <div className="mt-6 space-y-6">
          <div className="card p-5">
            <CompareHeader quotes={quotes} />
          </div>
          <div>
            <div className="text-xs tracking-widest text-muted uppercase mb-2">
              Per-bucket hours
            </div>
            <CompareBucketsChart quotes={quotes} />
          </div>
          <div className="card p-0 overflow-hidden">
            <div className="p-4 text-xs tracking-widest text-muted uppercase border-b border-border">
              Input differences
            </div>
            <CompareInputDiff quotes={quotes} />
          </div>
          <div>
            <div className="text-xs tracking-widest text-muted uppercase mb-2">Drivers</div>
            <CompareDriversStrip quotes={quotes} />
          </div>
        </div>
      )}
    </>
  );
}
