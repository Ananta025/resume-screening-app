"use client";

import type { Candidate } from "@/types/candidate";
import { ScoreBadge } from "./ScoreBadge";

interface CandidateTableProps {
  candidates: Candidate[];
  currentPage: number;
  pageSize: number;
  totalCandidates: number;
  onPageChange: (page: number) => void;
  onViewCandidate: (candidate: Candidate) => void;
}

export function CandidateTable({
  candidates,
  currentPage,
  pageSize,
  totalCandidates,
  onPageChange,
  onViewCandidate,
}: CandidateTableProps) {
  const totalPages = Math.max(1, Math.ceil(totalCandidates / pageSize));

  return (
    <div className="overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-[0_16px_50px_rgba(15,23,42,0.06)]">
      <div className="border-b border-slate-200 px-6 py-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-950">Candidate Rankings</h3>
            <p className="text-sm text-slate-500">Review the highest-ranked candidates and open detailed previews.</p>
          </div>
          <p className="text-sm text-slate-500">
            Showing {candidates.length} of {totalCandidates} candidates
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50/80">
            <tr className="text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              <th className="px-6 py-4">Rank</th>
              <th className="px-6 py-4">Candidate Name</th>
              <th className="px-6 py-4">Match Score</th>
              <th className="px-6 py-4">Matching Skills</th>
              <th className="px-6 py-4">Missing Skills</th>
              <th className="px-6 py-4">Resume Preview</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {candidates.map((candidate) => (
              <tr key={candidate.id} className="transition hover:bg-slate-50/80">
                <td className="px-6 py-5 text-sm font-semibold text-slate-900">#{candidate.rank}</td>
                <td className="px-6 py-5">
                  <div>
                    <p className="text-sm font-semibold text-slate-950">{candidate.name}</p>
                    <p className="text-xs text-slate-500">Experience Score: {candidate.experienceScore}% • Education Score: {candidate.educationScore}%</p>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <div className="flex min-w-44 flex-col gap-2">
                    <div className="flex items-center gap-3">
                      <ScoreBadge score={candidate.score} />
                      <span className="text-sm font-semibold text-slate-900">{candidate.score}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-100">
                      <div className="h-2 rounded-full bg-gradient-to-r from-slate-950 to-sky-600" style={{ width: `${candidate.score}%` }} />
                    </div>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <div className="flex flex-wrap gap-2">
                    {candidate.matchingSkills.map((skill) => (
                      <span key={skill} className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                        {skill}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-6 py-5">
                  <div className="flex flex-wrap gap-2">
                    {candidate.missingSkills.map((skill) => (
                      <span key={skill} className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
                        {skill}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-6 py-5">
                  <button
                    type="button"
                    onClick={() => onViewCandidate(candidate)}
                    className="inline-flex h-10 items-center justify-center rounded-full border border-slate-300 px-4 text-sm font-semibold text-slate-700 transition hover:border-slate-950 hover:bg-slate-950 hover:text-white"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-col gap-3 border-t border-slate-200 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Page {currentPage} of {totalPages}
        </p>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={currentPage === 1}
            onClick={() => onPageChange(currentPage - 1)}
            className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition disabled:cursor-not-allowed disabled:opacity-40 hover:bg-slate-50"
          >
            Previous
          </button>
          <button
            type="button"
            disabled={currentPage === totalPages}
            onClick={() => onPageChange(currentPage + 1)}
            className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition disabled:cursor-not-allowed disabled:opacity-40 hover:bg-slate-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}