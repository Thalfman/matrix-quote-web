import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/api/client";
import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";

type DemoStatus = { is_demo: boolean; enabled_env: boolean; has_real_data: boolean };
type LoadResponse = { loaded: boolean; reason: string | null };

export function UploadTrain() {
  const qc = useQueryClient();

  const { data: status } = useQuery<DemoStatus>({
    queryKey: ["demoStatus"],
    queryFn: async () => (await api.get<DemoStatus>("/demo/status")).data,
  });

  const load = useMutation<LoadResponse, unknown, void>({
    mutationFn: async () => (await api.post<LoadResponse>("/admin/demo/load")).data,
    onSuccess: (r) => {
      if (r.loaded) {
        toast.success("Demo data loaded. Reload the app to see estimates.");
        qc.invalidateQueries();
      } else {
        toast.error(r.reason ?? "Could not load demo data.");
      }
    },
  });

  return (
    <>
      {/* Demo data card */}
      <div className="card p-4 flex items-center justify-between mb-6">
        <div>
          <div className="text-[10px] tracking-widest text-muted font-semibold uppercase">
            Demo
          </div>
          <div className="text-ink text-sm">
            Load a synthetic dataset + pretrained models so every screen works.
          </div>
          {status?.has_real_data && (
            <div className="mt-1 text-xs text-warning">
              Real data is already present — demo load is disabled to avoid clobbering it.
            </div>
          )}
        </div>
        <button
          type="button"
          disabled={status?.has_real_data || load.isPending}
          onClick={() => load.mutate()}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-brand text-brand-foreground text-sm font-medium disabled:bg-steel-200 disabled:text-muted disabled:cursor-not-allowed"
        >
          <Sparkles size={16} strokeWidth={1.75} />
          Load demo data
        </button>
      </div>

      <PageHeader
        eyebrow="Admin"
        title="Upload & Train"
        description="Upload the latest project-hours Excel export, merge into master, and retrain all per-operation models."
      />
      <EmptyState
        title="Training workflow pending"
        body="File upload + progress UI land in a later slice."
      />
    </>
  );
}
