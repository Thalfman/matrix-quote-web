import { useInsightsOverview } from "@/api/quote";
import { PageHeader } from "@/components/PageHeader";

import { KpiCards } from "./insights/KpiCards";
import { QuotesActivityChart } from "./insights/QuotesActivityChart";
import { LatestQuotesTable } from "./insights/LatestQuotesTable";
import { AccuracyHeatmap } from "./insights/AccuracyHeatmap";

export function ExecutiveOverview() {
  const { data } = useInsightsOverview();

  return (
    <>
      <PageHeader
        eyebrow="Insights"
        title="Executive Overview"
        description="Pipeline activity, model accuracy, and per-operation trends at a glance."
      />
      <div className="mt-6 space-y-6">
        <KpiCards data={data} />
        <QuotesActivityChart rows={data?.quotes_activity ?? []} />
        <LatestQuotesTable rows={data?.latest_quotes ?? []} />
        <AccuracyHeatmap
          operations={data?.operations ?? []}
          quarters={data?.quarters ?? []}
          matrix={data?.accuracy_heatmap ?? []}
        />
      </div>
    </>
  );
}
