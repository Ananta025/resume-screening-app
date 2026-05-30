"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { JDInput } from "@/components/JDInput";
import { LoadingOverlay } from "@/components/LoadingOverlay";
import { StatCard } from "@/components/StatCard";
import { UploadZone } from "@/components/UploadZone";
import { clearAnalysisCache, fetchLatestAnalysis } from "@/services/api";
import type { CandidateAnalysisSummary } from "@/types/candidate";
import type { UploadedDocument } from "@/types/job";
import { useScreeningSubmission } from "@/hooks/useScreeningSubmission";

const DEFAULT_JD = "We are looking for a senior frontend engineer who can build scalable React applications, collaborate with product teams, and contribute to cloud-friendly delivery processes.";

export function ScreeningWorkspace() {
  const router = useRouter();
  const [resumes, setResumes] = useState<UploadedDocument[]>([]);
  const [jobDescription, setJobDescription] = useState(DEFAULT_JD);
  const [jdFile, setJdFile] = useState<UploadedDocument | undefined>();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [summary, setSummary] = useState<CandidateAnalysisSummary>({
    totalResumes: 0,
    candidatesProcessed: 0,
    averageScore: 0,
    topScore: 0,
  });
  const { submit, isSubmitting } = useScreeningSubmission();

  useEffect(() => {
    let isMounted = true;

    fetchLatestAnalysis()
      .then((analysis) => {
        if (isMounted) {
          setSummary(analysis.summary);
        }
      })
      .catch(() => {
        if (isMounted) {
          setSummary({
            totalResumes: 0,
            candidatesProcessed: 0,
            averageScore: 0,
            topScore: 0,
          });
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  async function handleAnalyze() {
    if (isAnalyzing || isSubmitting) {
      return;
    }

    setIsAnalyzing(true);
    try {
      const analysis = await submit({
        resumes,
        jobDescription: {
          description: jobDescription,
          file: jdFile?.file,
          fileName: jdFile?.name,
        },
      });
      setSummary(analysis.summary);
      router.push("/results");
    } catch {
      // toast is handled by the hook
    } finally {
      setIsAnalyzing(false);
    }
  }

  function handleReset() {
    setResumes([]);
    setJobDescription(DEFAULT_JD);
    setJdFile(undefined);
    clearAnalysisCache();
    setSummary((current) => ({ ...current, totalResumes: 0 }));
  }

  const canAnalyze = !isSubmitting && !isAnalyzing && resumes.length > 0 && jobDescription.trim().length > 0;

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
      <section className="relative overflow-hidden rounded-4xl border border-slate-200 bg-white/80 p-5 shadow-[0_20px_50px_rgba(15,23,42,0.08)] backdrop-blur sm:p-6">
        {isSubmitting ? <LoadingOverlay /> : null}
        <div className="flex flex-col gap-3 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">Screening workspace</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Upload resumes and score candidates</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">Uploads, analysis, and ranking now flow directly through the FastAPI backend.</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
            <p className="font-semibold text-slate-950">Accepted formats</p>
            <p>PDF, DOC, DOCX</p>
          </div>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="space-y-6">
            <UploadZone
              title="Upload Resumes"
              description="Add multiple candidate resumes using drag and drop or file browsing."
              accept=".pdf,.doc,.docx"
              multiple
              files={resumes}
              onFilesChange={setResumes}
              onRemoveFile={(fileId) => setResumes((current) => current.filter((file) => file.id !== fileId))}
            />

            <JDInput value={jobDescription} onChange={setJobDescription} fileName={jdFile?.name} onFileChange={setJdFile} />

            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={!canAnalyze}
                className="inline-flex h-12 items-center justify-center rounded-full bg-slate-950 px-6 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-slate-300 hover:bg-slate-800"
              >
                {isAnalyzing || isSubmitting ? "Analyzing..." : "Analyze Candidates"}
              </button>
              <button
                type="button"
                onClick={handleReset}
                disabled={isSubmitting}
                className="inline-flex h-12 items-center justify-center rounded-full border border-slate-300 px-6 text-sm font-semibold text-slate-700 transition disabled:cursor-not-allowed disabled:opacity-50 hover:bg-slate-50"
              >
                Reset
              </button>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
            <StatCard label="Total Resumes" value={resumes.length} hint="Uploaded files queued for screening" />
            <StatCard label="Candidates Processed" value={summary.candidatesProcessed} hint="Results generated by the analysis engine" />
            <StatCard label="Average Score" value={`${summary.averageScore}%`} hint="Mean match score across the latest run" />
            <StatCard label="Top Score" value={`${summary.topScore}%`} hint="Highest-ranked candidate in the shortlist" />
          </div>
        </div>
      </section>
    </main>
  );
}