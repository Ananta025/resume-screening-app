"use client";

import { useEffect } from "react";
import type { Candidate } from "@/types/candidate";
import { ScoreBadge } from "./ScoreBadge";

interface ResumePreviewModalProps {
  candidate: Candidate | null;
  resumePdfUrl: string | null;
  detailError: string | null;
  open: boolean;
  loading?: boolean;
  onClose: () => void;
}

export function ResumePreviewModal({ candidate, resumePdfUrl, detailError, open, loading = false, onClose }: ResumePreviewModalProps) {
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    if (open) {
      window.addEventListener("keydown", handleEscape);
    }

    return () => window.removeEventListener("keydown", handleEscape);
  }, [onClose, open]);

  if (!open || !candidate) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 px-4 py-8 backdrop-blur-sm">
      <div className="max-h-[90vh] w-full max-w-5xl overflow-y-auto rounded-[2rem] bg-white p-6 shadow-2xl sm:p-8">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">Candidate details</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">{candidate.name}</h2>
          </div>
          <button type="button" onClick={onClose} className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
            Close
          </button>
        </div>

        {loading ? (
          <div className="mt-6 rounded-[1.5rem] border border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-600">
            Loading candidate details...
          </div>
        ) : null}

        {!loading ? (
          <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-900">Resume Document</p>
                <ScoreBadge score={candidate.score} />
              </div>

              <div className="mt-4 overflow-hidden rounded-[1.5rem] border border-slate-200 bg-white">
                {detailError ? (
                  <div className="m-4 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{detailError}</div>
                ) : null}

                {resumePdfUrl ? (
                  <iframe
                    title={`Resume document for ${candidate.name}`}
                    src={resumePdfUrl}
                    className="h-[36rem] w-full"
                  />
                ) : (
                  <div className="m-4 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">Resume document unavailable.</div>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <InfoCard label="Match Score" value={`${candidate.score}%`} />
                <InfoCard label="Experience Score" value={`${candidate.experienceScore}%`} />
              </div>
              <InfoCard label="Education Score" value={`${candidate.educationScore}%`} />
              <SkillPanel title="Matching Skills" items={candidate.matchingSkills} tone="emerald" />
              <SkillPanel title="Missing Skills" items={candidate.missingSkills} tone="amber" />
              <div className="rounded-[1.25rem] border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">AI Summary</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">{candidate.summary}</p>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[1.25rem] border border-slate-200 bg-white p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">{label}</p>
      <p className="mt-2 text-base font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function SkillPanel({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone: "emerald" | "amber";
}) {
  const colorClasses = tone === "emerald" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700";

  return (
    <div className="rounded-[1.25rem] border border-slate-200 bg-white p-4">
      <p className="text-sm font-semibold text-slate-900">{title}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.map((item) => (
          <span key={item} className={`rounded-full px-3 py-1 text-xs font-semibold ${colorClasses}`}>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
