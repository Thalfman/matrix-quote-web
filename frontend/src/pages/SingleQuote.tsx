import { useEffect, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { api } from "@/api/client";
import { useDropdowns, useSingleQuote } from "@/api/quote";
import { ExplainedQuoteResponse, HealthResponse } from "@/api/types";
import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";

import { QuoteForm } from "./single-quote/QuoteForm";
import { QuoteResults } from "./single-quote/QuoteResults";
import {
  QuoteFormValues,
  SalesBucket,
  quoteFormDefaults,
  quoteFormSchema,
  transformToQuoteInput,
} from "./single-quote/schema";

export function SingleQuote() {
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: async () => (await api.get<HealthResponse>("/health")).data,
  });
  const { data: dropdowns } = useDropdowns();
  const mutate = useSingleQuote();

  const form = useForm<QuoteFormValues>({
    resolver: zodResolver(quoteFormSchema),
    defaultValues: quoteFormDefaults,
    mode: "onBlur",
  });

  const [result, setResult] = useState<ExplainedQuoteResponse | null>(null);
  const [quotedHoursByBucket, setQuotedHoursByBucket] = useState<Partial<Record<SalesBucket, number>>>({});

  // Seed categorical defaults from the dropdown catalog once it loads (so the
  // user doesn't have to touch every dropdown just to fire off an estimate).
  useEffect(() => {
    if (!dropdowns) return;
    const current = form.getValues();
    const patch: Partial<QuoteFormValues> = {};
    if (!current.industry_segment && dropdowns.industry_segment[0])
      patch.industry_segment = dropdowns.industry_segment[0];
    if (!current.system_category && dropdowns.system_category[0])
      patch.system_category = dropdowns.system_category[0];
    if (!current.automation_level && dropdowns.automation_level[0])
      patch.automation_level = dropdowns.automation_level[0];
    if (Object.keys(patch).length) form.reset({ ...current, ...patch });
  }, [dropdowns, form]);

  const modelsReady = health?.models_ready ?? false;

  if (!modelsReady) {
    return (
      <>
        <PageHeader
          eyebrow="Estimate"
          title="Single Quote"
          description="Enter quote-time project parameters to generate an hour estimate with confidence intervals per sales bucket."
          chips={[{ label: "Models not trained", tone: "warning" }]}
        />
        <EmptyState
          title="Models are not trained"
          body="An admin needs to upload a project-hours dataset and train the per-operation models before quotes can be generated."
        />
      </>
    );
  }

  async function handleSubmit(quoted: Partial<Record<SalesBucket, number>>) {
    const values = form.getValues();
    const payload = transformToQuoteInput(values);
    try {
      const result = await mutate.mutateAsync(payload);
      setResult(result);
      setQuotedHoursByBucket(quoted);
      // Scroll to results once rendered.
      requestAnimationFrame(() => {
        document.getElementById("quote-results")?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to generate estimate";
      toast.error(detail);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Estimate"
        title="Single Quote"
        description="Enter quote-time project parameters to generate an hour estimate with confidence intervals per sales bucket."
        chips={[{ label: "Models ready", tone: "success" }]}
      />

      <QuoteForm
        dropdowns={dropdowns}
        submitting={mutate.isPending}
        onSubmit={handleSubmit}
        form={form}
      />

      {result && (
        <div id="quote-results">
          <QuoteResults result={result} quotedHoursByBucket={quotedHoursByBucket} />
        </div>
      )}
    </>
  );
}
