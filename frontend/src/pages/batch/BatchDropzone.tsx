import { ChangeEvent, DragEvent, useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { toast } from "sonner";

export function BatchDropzone() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [hover, setHover] = useState(false);

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setHover(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      toast.info(`Received "${file.name}" · batch inference lands later`);
    }
  };

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      toast.info(`Received "${file.name}" · batch inference lands later`);
    }
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setHover(true);
      }}
      onDragLeave={() => setHover(false)}
      onDrop={onDrop}
      className={
        "card p-8 flex flex-col items-center justify-center gap-4 text-center " +
        "border-dashed border-line2 transition-colors " +
        (hover ? "bg-paper border-teal" : "bg-paper/40 hover:bg-paper")
      }
    >
      <div
        aria-hidden="true"
        className="w-14 h-14 rounded-sm bg-ink text-white grid place-items-center"
      >
        <UploadCloud size={22} strokeWidth={1.5} />
      </div>
      <div>
        <div className="display-hero text-lg text-ink">Drop a CSV or XLSX</div>
        <div className="text-xs text-muted mt-1 max-w-sm mx-auto">
          Up to 500 rows per batch. First header row must match the schema on the right. Duplicate
          project names are flagged but not dropped.
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="inline-flex items-center gap-2 px-4 py-2 bg-ink text-white text-sm font-medium rounded-sm hover:bg-ink2"
        >
          Select file
        </button>
        <button
          type="button"
          onClick={() =>
            toast.info("Template download lands when the batch endpoint ships")
          }
          className="inline-flex items-center gap-2 px-3 py-2 text-xs border hairline rounded-sm bg-surface hover:bg-paper"
        >
          Download template
        </button>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx"
        onChange={onChange}
        className="hidden"
        aria-hidden="true"
      />
    </div>
  );
}
