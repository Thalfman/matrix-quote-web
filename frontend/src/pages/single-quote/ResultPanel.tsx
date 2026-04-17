// frontend/src/pages/single-quote/ResultPanel.tsx
import { Download, Save } from "lucide-react";
import { ExplainedQuoteResponse } from "@/api/types";
import { HeroEstimate } from "./HeroEstimate";
import { ResultTabs } from "./ResultTabs";
import { ResultSkeleton } from "./ResultSkeleton";
import { Scenario } from "./Scenario";

type Props = {
  result: ExplainedQuoteResponse | null;
  isLoading: boolean;
  scenarios: Scenario[];
  onSaveScenario: () => void;
  onExportPdf: () => void;
  onRemoveScenario: (id: string) => void;
  onCompare: () => void;
};

export function ResultPanel({
  result,
  isLoading,
  scenarios,
  onSaveScenario,
  onExportPdf,
  onRemoveScenario,
  onCompare,
}: Props) {
  if (isLoading) return <ResultSkeleton />;

  if (!result) {
    return (
      <div className="card p-8">
        <div className="text-[10px] tracking-widest text-muted font-semibold">
          RESULTS
        </div>
        <p className="mt-3 text-ink">Fill the form and generate an estimate.</p>
        <p className="mt-1 text-sm text-muted">
          You'll see confidence intervals, drivers, and similar past projects here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4" id="quote-results">
      <HeroEstimate result={result} />
      <ResultTabs
        result={result}
        scenarios={scenarios}
        onRemoveScenario={onRemoveScenario}
        onCompare={onCompare}
      />
      <div className="flex gap-2">
        <button
          type="button"
          onClick={onSaveScenario}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-brand text-brand-foreground text-sm font-medium hover:bg-brand-hover transition-colors"
        >
          <Save size={16} strokeWidth={1.75} />
          Save scenario
        </button>
        <button
          type="button"
          onClick={onExportPdf}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md border border-border text-ink text-sm font-medium hover:bg-steel-100 transition-colors"
        >
          <Download size={16} strokeWidth={1.75} />
          Export PDF
        </button>
      </div>
    </div>
  );
}
