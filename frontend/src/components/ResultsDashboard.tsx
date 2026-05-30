"use client";

import { useMemo, useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { CandidateTable } from "@/components/CandidateTable";
import { EmptyState } from "@/components/EmptyState";
import { ResumePreviewModal } from "@/components/ResumePreviewModal";
import { LoadingOverlay } from "@/components/LoadingOverlay";
import { ScoreBadge } from "@/components/ScoreBadge";
import { downloadResultsAsCSV, downloadResultsAsExcel, fetchResumeFileByResumeId, sortAnalysisCandidates } from "@/services/api";
import type { Candidate, CandidateSortOption } from "@/types/candidate";
import { useAnalysisResults } from "@/hooks/useAnalysisResults";
import { useToast } from "@/hooks/useToast";

const PAGE_SIZE = 5;

export function ResultsDashboard() {
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<CandidateSortOption>("score-desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [selectedResumePdfUrl, setSelectedResumePdfUrl] = useState<string | null>(null);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const { data: analysis, isLoading, error, refresh, getById } = useAnalysisResults();
  const toast = useToast();

  const filteredCandidates = useMemo(() => {
    const candidates = analysis?.candidates ?? [];
    const uniqueCandidates = candidates.filter(
      (item, index, self) => index === self.findIndex((candidate) => candidate.resumeId === item.resumeId),
    );
    const query = search.trim().toLowerCase();
    const searched = query
      ? uniqueCandidates.filter((candidate) => {
          const haystack = [
            candidate.name,
            `${candidate.experienceScore}`,
            `${candidate.educationScore}`,
            ...candidate.matchingSkills,
            ...candidate.missingSkills,
          ]
            .join(" ")
            .toLowerCase();
          return haystack.includes(query);
        })
      : uniqueCandidates;

    return sortAnalysisCandidates(searched, sortBy);
  }, [analysis?.candidates, search, sortBy]);

  const totalPages = Math.max(1, Math.ceil(filteredCandidates.length / PAGE_SIZE));
  const effectivePage = Math.min(currentPage, totalPages);
  const paginatedCandidates = filteredCandidates.slice((effectivePage - 1) * PAGE_SIZE, effectivePage * PAGE_SIZE);
  const summary = analysis?.summary;

  async function handleViewCandidate(candidate: Candidate) {
    console.debug("Candidate view clicked", { analysis_result_id: candidate.id, resume_id: candidate.resumeId });
    setSelectedCandidate(candidate);
    setSelectedResumePdfUrl(null);
    setDetailError(null);
    setIsDetailLoading(true);

    try {
      const detail = await getById(candidate.id);
      setSelectedCandidate(detail);
      const resumeId = detail.resumeId ?? candidate.resumeId;

      if (!resumeId) {
        throw new Error("resume_id missing in candidate details response");
      }

      console.debug("resume_id received", { resume_id: resumeId });
      const fileResponse = await fetchResumeFileByResumeId(resumeId);
      setSelectedResumePdfUrl(fileResponse.pdf_url);
      console.debug("PDF URL loaded successfully", { resume_id: resumeId, pdf_url: fileResponse.pdf_url });
    } catch {
      setDetailError("Unable to load resume document for this candidate.");
      toast.error("Unable to load candidate details", "Resume document could not be loaded.");
    } finally {
      setIsDetailLoading(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-6 xl:grid-cols-[280px_1fr]">
        <div className="xl:sticky xl:top-24 xl:self-start">
          <Sidebar />
          <div className="mt-6 rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-[0_16px_45px_rgba(15,23,42,0.06)]">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">Current snapshot</p>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <div className="flex items-center justify-between">
                <span>Processed</span>
                <span className="font-semibold text-slate-950">{summary?.candidatesProcessed ?? 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Top score</span>
                <span className="font-semibold text-slate-950">{summary ? `${summary.topScore}%` : "0%"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Status</span>
                <ScoreBadge score={summary?.averageScore ?? 0} />
              </div>
            </div>
          </div>
        </div>

        <section className="relative space-y-6">
          {isLoading ? <LoadingOverlay label="Loading ranked candidates..." /> : null}
          {error ? (
            <div className="rounded-3xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
              <div className="flex items-center justify-between gap-3">
                <span>{error}</span>
                <button
                  type="button"
                  onClick={() => void refresh()}
                  className="rounded-full border border-rose-300 px-4 py-2 text-sm font-semibold text-rose-700 transition hover:bg-rose-100"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : null}
          <div className="rounded-4xl border border-slate-200 bg-white/80 p-5 shadow-[0_20px_50px_rgba(15,23,42,0.08)] backdrop-blur sm:p-6">
            <div className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">Results dashboard</p>
                <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Candidate Rankings</h1>
                <p className="mt-2 text-sm leading-6 text-slate-600">Search, sort, export, and review candidate matches in one dashboard.</p>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <button type="button" onClick={() => downloadResultsAsCSV(filteredCandidates)} className="inline-flex h-11 items-center justify-center rounded-full border border-slate-300 px-5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
                  Export CSV
                </button>
                <button type="button" onClick={() => downloadResultsAsExcel(filteredCandidates)} className="inline-flex h-11 items-center justify-center rounded-full bg-slate-950 px-5 text-sm font-semibold text-white transition hover:bg-slate-800">
                  Export Excel
                </button>
              </div>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <label className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Search Candidate</label>
                <input
                  value={search}
                  onChange={(event) => {
                    setSearch(event.target.value);
                    setCurrentPage(1);
                  }}
                  placeholder="Search by name, skills, education, or experience"
                  className="mt-3 w-full rounded-[1.25rem] border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-900"
                />
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <label className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Sort by Score</label>
                <select
                  value={sortBy}
                  onChange={(event) => {
                    setSortBy(event.target.value as CandidateSortOption);
                    setCurrentPage(1);
                  }}
                  className="mt-3 w-full rounded-[1.25rem] border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-900"
                >
                  <option value="score-desc">Highest score first</option>
                  <option value="score-asc">Lowest score first</option>
                  <option value="rank">Rank</option>
                  <option value="name">Candidate name</option>
                </select>
              </div>
            </div>
          </div>

          {paginatedCandidates.length ? (
            <CandidateTable
              candidates={paginatedCandidates}
              currentPage={effectivePage}
              pageSize={PAGE_SIZE}
              totalCandidates={filteredCandidates.length}
              onPageChange={setCurrentPage}
              onViewCandidate={handleViewCandidate}
            />
          ) : (
            <EmptyState
              title="No candidates found"
              description="Try a different search term or return to the screening page to analyze another batch of resumes."
              actionHref="/screening"
              actionLabel="Go to Screening"
            />
          )}
        </section>
      </div>

      <ResumePreviewModal
        candidate={selectedCandidate}
        resumePdfUrl={selectedResumePdfUrl}
        detailError={detailError}
        open={Boolean(selectedCandidate)}
        loading={isDetailLoading}
        onClose={() => {
          setSelectedCandidate(null);
          setSelectedResumePdfUrl(null);
          setDetailError(null);
        }}
      />
    </main>
  );
}