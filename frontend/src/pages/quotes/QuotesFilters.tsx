import { Search } from "lucide-react";

type Props = {
  projects: string[];
  industries: string[];
  project: string | null;
  industry: string | null;
  search: string;
  onChange: (next: { project: string | null; industry: string | null; search: string }) => void;
};

export function QuotesFilters({ projects, industries, project, industry, search, onChange }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <select
        value={project ?? ""}
        onChange={(e) => onChange({ project: e.target.value || null, industry, search })}
        className="bg-surface border border-border rounded-md px-2 py-1.5 text-sm"
      >
        <option value="">All projects</option>
        {projects.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <select
        value={industry ?? ""}
        onChange={(e) => onChange({ project, industry: e.target.value || null, search })}
        className="bg-surface border border-border rounded-md px-2 py-1.5 text-sm"
      >
        <option value="">All industries</option>
        {industries.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <div className="relative">
        <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted" />
        <input
          type="search"
          value={search}
          onChange={(e) => onChange({ project, industry, search: e.target.value })}
          placeholder="Search name, project, client"
          className="bg-surface border border-border rounded-md pl-7 pr-2 py-1.5 text-sm w-64"
        />
      </div>
    </div>
  );
}
