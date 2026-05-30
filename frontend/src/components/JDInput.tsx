"use client";

import { useRef } from "react";
import type { UploadedDocument } from "@/types/job";

interface JDInputProps {
  value: string;
  onChange: (value: string) => void;
  fileName?: string;
  onFileChange: (file?: UploadedDocument) => void;
}

export function JDInput({ value, onChange, fileName, onFileChange }: JDInputProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  function handleUpload(file: File | null) {
    if (!file) {
      return;
    }

    onFileChange({
      id: `${file.name}-${file.size}-${file.lastModified}`,
      name: file.name,
      size: file.size,
      type: file.type,
      file,
    });
  }

  return (
    <section className="rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-[0_16px_45px_rgba(15,23,42,0.06)]">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-950">Job Description</h3>
          <p className="mt-1 text-sm text-slate-500">Paste the role requirements or upload a JD file.</p>
        </div>
        <button type="button" onClick={() => inputRef.current?.click()} className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
          Upload JD file
        </button>
      </div>

      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Paste responsibilities, required skills, years of experience, and any role-specific screening criteria..."
        className="mt-4 min-h-56 w-full rounded-[1.5rem] border border-slate-300 bg-slate-50 px-4 py-4 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-900 focus:bg-white"
      />

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-500">
        <span>{value.length} characters</span>
        <div className="flex items-center gap-3">
          {fileName ? (
            <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">JD file: {fileName}</span>
          ) : (
            <span className="text-xs text-slate-400">No JD file uploaded</span>
          )}
          <button
            type="button"
            onClick={() => onFileChange(undefined)}
            disabled={!fileName}
            className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 transition disabled:cursor-not-allowed disabled:opacity-40 hover:bg-slate-50"
          >
            Clear file
          </button>
        </div>
      </div>

      <input ref={inputRef} type="file" accept=".pdf,.doc,.docx" className="hidden" onChange={(event) => handleUpload(event.target.files?.[0] ?? null)} />
    </section>
  );
}