"use client";

import { useRef, useState } from "react";
import { formatSize } from "@/lib/utils";
import type { UploadedDocument } from "@/types/job";

interface UploadZoneProps {
  title: string;
  description: string;
  accept: string;
  multiple?: boolean;
  files: UploadedDocument[];
  onFilesChange: (files: UploadedDocument[]) => void;
  onRemoveFile: (fileId: string) => void;
}

export function UploadZone({
  title,
  description,
  accept,
  multiple = true,
  files,
  onFilesChange,
  onRemoveFile,
}: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleFiles(selectedFiles: FileList | null) {
    if (!selectedFiles?.length) {
      return;
    }

    const nextFiles = Array.from(selectedFiles).map((file) => ({
      id: `${file.name}-${file.size}-${file.lastModified}`,
      name: file.name,
      size: file.size,
      type: file.type,
      file,
    }));

    onFilesChange(multiple ? [...files, ...nextFiles] : nextFiles.slice(0, 1));

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  return (
    <section className="rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-[0_16px_45px_rgba(15,23,42,0.06)]">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-950">{title}</h3>
          <p className="mt-1 text-sm text-slate-500">{description}</p>
        </div>
        <button type="button" onClick={() => inputRef.current?.click()} className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
          Browse files
        </button>
      </div>

      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          handleFiles(event.dataTransfer.files);
        }}
        className={`mt-4 rounded-[1.5rem] border-2 border-dashed p-6 text-center transition ${isDragging ? "border-slate-900 bg-slate-50" : "border-slate-300 bg-slate-50/80"}`}
      >
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-xl shadow-sm">⬆</div>
        <p className="mt-4 text-sm font-medium text-slate-900">Drop files here or click to upload</p>
        <p className="mt-1 text-xs text-slate-500">Supported formats: PDF, DOC, DOCX</p>
        <input ref={inputRef} type="file" accept={accept} multiple={multiple} className="hidden" onChange={(event) => handleFiles(event.target.files)} />
      </div>

      <div className="mt-4 space-y-3">
        {files.length ? (
          files.map((file) => (
            <div key={file.id} className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
              <div>
                <p className="text-sm font-medium text-slate-900">{file.name}</p>
                <p className="text-xs text-slate-500">{formatSize(file.size)}</p>
              </div>
              <button
                type="button"
                onClick={() => onRemoveFile(file.id)}
                className="rounded-full border border-transparent px-3 py-1 text-xs font-semibold text-rose-600 transition hover:border-rose-200 hover:bg-rose-50"
              >
                Remove
              </button>
            </div>
          ))
        ) : (
          <p className="rounded-2xl border border-dashed border-slate-200 px-4 py-6 text-center text-sm text-slate-500">No files uploaded yet.</p>
        )}
      </div>
    </section>
  );
}