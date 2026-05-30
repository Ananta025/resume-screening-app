export interface Candidate {
  id: number;
  resumeId?: number;
  jdId?: number;
  name: string;
  score: number;
  finalScore?: number;
  rank: number;
  matchingSkills: string[];
  missingSkills: string[];
  experienceScore: number;
  educationScore: number;
  summary: string;
  semanticScore?: number;
  createdAt?: string;
}

export interface CandidateAnalysisSummary {
  totalResumes: number;
  candidatesProcessed: number;
  averageScore: number;
  topScore: number;
}

export interface CandidateAnalysisResult {
  candidates: Candidate[];
  summary: CandidateAnalysisSummary;
  generatedAt: string;
}

export type CandidateSortOption = "score-desc" | "score-asc" | "rank" | "name";