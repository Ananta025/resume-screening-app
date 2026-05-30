import { Packer, Document, Paragraph } from "docx";
import type { Candidate, CandidateAnalysisResult, CandidateSortOption } from "@/types/candidate";
import type { ScreeningRequest } from "@/types/job";
import type {
  AnalysisResponseApi,
  AnalysisResultApi,
  ResumeFileResponse,
  UploadedFileInfoApi,
  UploadContext,
  UploadResponseApi,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const UPLOAD_CONTEXT_KEY = "resume-screening-upload-context";
let latestAnalysisPromise: Promise<CandidateAnalysisResult> | null = null;

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

function buildUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

function generateAnalysisRequestId() {
  return globalThis.crypto?.randomUUID?.() ?? `analysis-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

async function readErrorResponse(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  try {
    return await response.text();
  } catch {
    return null;
  }
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const details = await readErrorResponse(response);
    const message =
      (typeof details === "object" && details !== null && "message" in details && typeof details.message === "string"
        ? details.message
        : null) ??
      (typeof details === "object" && details !== null && "detail" in details && typeof details.detail === "string"
        ? details.detail
        : null) ??
      response.statusText ??
      "Request failed";

    throw new ApiError(message, response.status, details);
  }

  return response.json() as Promise<T>;
}

function parseJsonStorage<T>(key: string): T | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.sessionStorage.getItem(key);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function saveJsonStorage<T>(key: string, value: T) {
  if (typeof window === "undefined") {
    return;
  }

  window.sessionStorage.setItem(key, JSON.stringify(value));
}

export function clearAnalysisCache() {
  if (typeof window === "undefined") {
    return;
  }

  window.sessionStorage.removeItem(UPLOAD_CONTEXT_KEY);
}

export function getUploadContext(): UploadContext | null {
  return parseJsonStorage<UploadContext>(UPLOAD_CONTEXT_KEY);
}

function saveUploadContext(context: UploadContext) {
  saveJsonStorage(UPLOAD_CONTEXT_KEY, context);
}

export function getCandidateNameByResumeId(resumeId: number) {
  return getUploadContext()?.resumeNames[String(resumeId)] ?? `Resume #${resumeId}`;
}

async function uploadResumes(files: File[]): Promise<UploadedFileInfoApi[]> {
  if (!files.length) {
    throw new ApiError("At least one resume file is required", 400);
  }

  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const response = await requestJson<UploadResponseApi>("/api/resumes/upload", {
    method: "POST",
    body: formData,
  });

  return response.uploaded_files;
}

async function uploadJobDescriptionFile(file: File, title?: string): Promise<UploadedFileInfoApi> {
  const formData = new FormData();
  formData.append("file", file);
  if (title) {
    formData.append("title", title);
  }

  const response = await requestJson<UploadResponseApi>("/api/jd/upload", {
    method: "POST",
    body: formData,
  });

  const [uploadedFile] = response.uploaded_files;
  if (!uploadedFile) {
    throw new ApiError("Job description upload did not return file metadata", 500);
  }

  return uploadedFile;
}

async function buildJobDescriptionFileFromText(text: string, fileName = "job-description.docx") {
  const doc = new Document({
    sections: [
      {
        children: [new Paragraph(text || "")],
      },
    ],
  });

  const blob = await Packer.toBlob(doc);
  return new File([blob], fileName, {
    type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  });
}

export async function uploadJobDescriptionInput(jobDescription: ScreeningRequest["jobDescription"]): Promise<UploadedFileInfoApi> {
  if (jobDescription.file) {
    return uploadJobDescriptionFile(jobDescription.file, jobDescription.fileName ?? jobDescription.file.name);
  }

  if (!jobDescription.description.trim()) {
    throw new ApiError("Job description is required", 400);
  }

  const file = await buildJobDescriptionFileFromText(jobDescription.description, `${jobDescription.fileName ?? "job-description"}.docx`);
  return uploadJobDescriptionFile(file, jobDescription.fileName ?? "Job Description");
}

export async function analyzeBackendCandidates(analysisRequestId: string) {
  return requestJson<AnalysisResponseApi>("/api/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ analysis_request_id: analysisRequestId }),
  });
}

export async function fetchResultsApi() {
  return requestJson<AnalysisResultApi[]>("/api/results");
}

export async function fetchResultByIdApi(id: number) {
  return requestJson<AnalysisResultApi>(`/api/results/${id}`);
}

export async function fetchResumeFileByResumeId(resumeId: number): Promise<ResumeFileResponse> {
  console.debug("Fetching resume file URL", { resume_id: resumeId });
  const response = await requestJson<ResumeFileResponse>(`/api/resumes/${resumeId}/file`);
  console.debug("Resume file URL API response received", { resume_id: resumeId, pdf_url: response.pdf_url });
  return response;
}

function buildSummary(candidates: Candidate[]): { totalResumes: number; candidatesProcessed: number; averageScore: number; topScore: number } {
  const averageScore = candidates.length
    ? Math.round(candidates.reduce((total, candidate) => total + candidate.score, 0) / candidates.length)
    : 0;

  return {
    totalResumes: candidates.length,
    candidatesProcessed: candidates.length,
    averageScore,
    topScore: candidates[0]?.score ?? 0,
  };
}

function summarizeCandidate(result: AnalysisResultApi): string {
  const matching = result.matching_skills.length ? result.matching_skills.join(", ") : "no matching skills";
  const missing = result.missing_skills.length ? result.missing_skills.join(", ") : "no major gaps";

  return `Final score ${result.final_score.toFixed(0)}%. Matching skills: ${matching}. Missing skills: ${missing}.`;
}

function mapResultToCandidate(result: AnalysisResultApi): Candidate {
  const score = Number(result.final_score ?? result.score ?? 0);
  const name = getCandidateNameByResumeId(result.resume_id);

  return {
    id: result.id,
    resumeId: result.resume_id,
    jdId: result.jd_id,
    name,
    score,
    finalScore: score,
    rank: result.rank,
    matchingSkills: result.matching_skills,
    missingSkills: result.missing_skills,
    experienceScore: result.experience_score,
    educationScore: result.education_score,
    summary: summarizeCandidate(result),
    semanticScore: result.semantic_score,
    createdAt: result.created_at,
  };
}

function sortCandidatesByScore(candidates: Candidate[], sortBy: CandidateSortOption) {
  const sorted = [...candidates];

  switch (sortBy) {
    case "score-asc":
      return sorted.sort((left, right) => left.score - right.score);
    case "name":
      return sorted.sort((left, right) => left.name.localeCompare(right.name));
    case "rank":
      return sorted.sort((left, right) => left.rank - right.rank);
    case "score-desc":
    default:
      return sorted.sort((left, right) => right.score - left.score);
  }
}

export async function fetchLatestAnalysis(): Promise<CandidateAnalysisResult> {
  if (latestAnalysisPromise) {
    return latestAnalysisPromise;
  }

  latestAnalysisPromise = (async () => {
    const response = await fetchResultsApi();
    const uniqueResults = response.filter(
      (item, index, self) => index === self.findIndex((candidate) => candidate.resume_id === item.resume_id),
    );
    const candidates = sortCandidatesByScore(uniqueResults.map(mapResultToCandidate), "score-desc");

    return {
      candidates,
      summary: buildSummary(candidates),
      generatedAt: candidates[0]?.createdAt ?? new Date().toISOString(),
    };
  })();

  try {
    return await latestAnalysisPromise;
  } finally {
    latestAnalysisPromise = null;
  }
}

export async function fetchAnalysisResultById(id: number): Promise<Candidate> {
  const result = await fetchResultByIdApi(id);
  return mapResultToCandidate(result);
}

export async function analyzeCandidateResumes(request: ScreeningRequest): Promise<CandidateAnalysisResult> {
  const analysisRequestId = request.analysisRequestId ?? generateAnalysisRequestId();
  const uploadedResumes = await uploadResumes(request.resumes.map((document) => {
    if (!document.file) {
      throw new ApiError(`Missing file for resume ${document.name}`, 400);
    }

    return document.file;
  }));

  const uploadedJobDescription = await uploadJobDescriptionInput(request.jobDescription);

  saveUploadContext({
    resumeNames: Object.fromEntries(uploadedResumes.map((file) => [String(file.id), file.display_name])),
    jdName: uploadedJobDescription.display_name,
    uploadedAt: new Date().toISOString(),
  });

  await analyzeBackendCandidates(analysisRequestId);
  return fetchLatestAnalysis();
}

export function sortAnalysisCandidates(candidates: CandidateAnalysisResult["candidates"], sortBy: CandidateSortOption) {
  return sortCandidatesByScore(candidates, sortBy);
}

export function downloadResultsAsCSV(candidates: CandidateAnalysisResult["candidates"]) {
  const header = ["Rank", "Candidate Name", "Match Score", "Matching Skills", "Missing Skills", "Experience Score", "Education Score"];
  const rows = candidates.map((candidate) => [
    candidate.rank,
    candidate.name,
    candidate.score,
    candidate.matchingSkills.join("; "),
    candidate.missingSkills.join("; "),
    `${candidate.experienceScore}%`,
    `${candidate.educationScore}%`,
  ]);

  const csv = [header, ...rows]
    .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","))
    .join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = "candidate-rankings.csv";
  anchor.click();
  window.URL.revokeObjectURL(url);
}

export function downloadResultsAsExcel(candidates: CandidateAnalysisResult["candidates"]) {
  const html = `
    <html>
      <head><meta charset="utf-8" /></head>
      <body>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Candidate Name</th>
              <th>Match Score</th>
              <th>Matching Skills</th>
              <th>Missing Skills</th>
              <th>Experience Score</th>
              <th>Education Score</th>
            </tr>
          </thead>
          <tbody>
            ${candidates
              .map(
                (candidate) => `
                <tr>
                  <td>${candidate.rank}</td>
                  <td>${candidate.name}</td>
                  <td>${candidate.score}</td>
                  <td>${candidate.matchingSkills.join(", ")}</td>
                  <td>${candidate.missingSkills.join(", ")}</td>
                  <td>${candidate.experienceScore}%</td>
                  <td>${candidate.educationScore}%</td>
                </tr>`,
              )
              .join("")}
          </tbody>
        </table>
      </body>
    </html>`;

  const blob = new Blob([html], { type: "application/vnd.ms-excel" });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = "candidate-rankings.xls";
  anchor.click();
  window.URL.revokeObjectURL(url);
}