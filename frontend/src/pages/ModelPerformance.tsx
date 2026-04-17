import {
  useCalibration, useMetricsHistory, usePerformanceHeadline,
} from "@/api/quote";
import { useQuery } from "@tanstack/react-query";

import { api } from "@/api/client";
import { MetricsSummary } from "@/api/types";
import { PageHeader } from "@/components/PageHeader";

import { HeadlineKPIs } from "./performance/HeadlineKPIs";
import { MapeByOperation } from "./performance/MapeByOperation";
import { CalibrationScatter } from "./performance/CalibrationScatter";
import { TrainingHistoryChart } from "./performance/TrainingHistoryChart";


export function ModelPerformance() {
  const { data: summary }    = useQuery({
    queryKey: ["metrics"],
    queryFn: async () => (await api.get<MetricsSummary>("/metrics")).data,
  });
  const { data: headline }   = usePerformanceHeadline();
  const { data: calibration} = useCalibration();
  const { data: history }    = useMetricsHistory();

  return (
    <>
      <PageHeader
        eyebrow="Insights"
        title="Estimate Accuracy"
        description="How well the model predicts actuals across operations, confidence bands, and training runs."
      />
      <div className="mt-6 space-y-6">
        <HeadlineKPIs head={headline} />
        <MapeByOperation rows={summary?.metrics ?? []} />
        <CalibrationScatter points={calibration ?? []} />
        <TrainingHistoryChart rows={history ?? []} />
      </div>
    </>
  );
}
