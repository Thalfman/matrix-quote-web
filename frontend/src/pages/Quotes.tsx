import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { useDeleteScenario, useDuplicateScenario, useSavedQuotes } from "@/api/quote";
import { PageHeader } from "@/components/PageHeader";

import { QuotesFilters } from "./quotes/QuotesFilters";
import { QuotesTable } from "./quotes/QuotesTable";

export function Quotes() {
  const [project, setProject] = useState<string | null>(null);
  const [industry, setIndustry] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const navigate = useNavigate();

  const query = useSavedQuotes({
    project: project ?? undefined,
    industry: industry ?? undefined,
    search: search || undefined,
  });
  const rows = query.data?.rows ?? [];

  const projects = useMemo(
    () => Array.from(new Set(rows.map((r) => r.project_name))).sort(),
    [rows],
  );
  const industries = useMemo(
    () => Array.from(new Set(rows.map((r) => r.industry_segment))).sort(),
    [rows],
  );

  const del = useDeleteScenario();
  const dup = useDuplicateScenario();

  const toggle = (id: string) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const compareSelected = () => {
    if (selected.size < 2 || selected.size > 3) return;
    navigate(`/quotes/compare?ids=${[...selected].join(",")}`);
  };

  return (
    <>
      <PageHeader
        eyebrow="Quotes"
        title="Saved Quotes"
        description="Every saved scenario, filterable and comparable."
      />
      <div className="mt-5 flex items-center justify-between gap-4 flex-wrap">
        <QuotesFilters
          projects={projects}
          industries={industries}
          project={project}
          industry={industry}
          search={search}
          onChange={({ project: p, industry: i, search: s }) => {
            setProject(p);
            setIndustry(i);
            setSearch(s);
          }}
        />
        <button
          type="button"
          onClick={compareSelected}
          disabled={selected.size < 2 || selected.size > 3}
          className="px-3 py-1.5 rounded-md bg-brand text-brand-foreground text-sm disabled:bg-steel-200 disabled:text-muted disabled:cursor-not-allowed"
        >
          Compare {selected.size > 0 ? selected.size : ""} selected
        </button>
      </div>
      <div className="mt-4">
        <QuotesTable
          rows={rows}
          selected={selected}
          onToggle={toggle}
          onRowAction={async (id, action) => {
            if (action === "duplicate") {
              const copy = await dup.mutateAsync(id);
              toast.success(`Duplicated as "${copy.name}"`);
            } else if (action === "delete") {
              if (!confirm("Delete this scenario?")) return;
              await del.mutateAsync(id);
              toast.success("Deleted");
            } else if (action === "pdf") {
              toast.info("PDF export lands in Plan D");
            } else if (action === "open") {
              toast.info("Opening saved quotes in the cockpit lands in a follow-up");
            }
          }}
        />
      </div>
    </>
  );
}
