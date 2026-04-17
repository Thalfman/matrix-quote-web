import { useEffect, useState } from "react";
import { getDisplayName, setDisplayName } from "@/lib/displayName";

function initials(name: string): string {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0]?.toUpperCase() ?? "")
      .join("") || "?"
  );
}

export function UserPill() {
  const [name, setName] = useState<string>("");
  useEffect(() => {
    setName(getDisplayName());
  }, []);
  return (
    <button
      type="button"
      onClick={() => {
        const next = prompt("Your display name (used to attribute quotes)", name) ?? "";
        if (next.trim()) {
          setDisplayName(next.trim());
          setName(next.trim());
        }
      }}
      className="inline-flex items-center gap-2 text-sm text-muted hover:text-ink transition-colors"
      aria-label="Edit display name"
    >
      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-accent/10 text-ink text-xs font-semibold">
        {initials(name || "Guest")}
      </span>
      <span className="hidden sm:inline">{name || "Set name"}</span>
    </button>
  );
}
