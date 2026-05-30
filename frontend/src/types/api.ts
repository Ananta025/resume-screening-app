export interface UploadedFileInfoApi {
  id: number;
  display_name: string;
  file_name: string;
  file_path: string;
  file_size: number;
  content_type: string | null;
  created_at: string;
}

export interface UploadResponseApi {
  success: boolean;
  uploaded_files: UploadedFileInfoApi[];
}

export interface AnalysisResult {
  id: number;
  resume_id: number;
  jd_id: number;
  analysis_request_id?: string | null;
  score: number;
  final_score: number;
  rank: number;
  skills_score: number;
  matching_skills: string[];
  missing_skills: string[];
  experience_score: number;
  education_score: number;
  semantic_score: number;
  score_breakdown?: {
    skills_score: number;
    experience_score: number;
    education_score: number;
    semantic_score: number;
    final_score: number;
  };
  created_at: string;
}

export type AnalysisResultApi = AnalysisResult;

export interface AnalysisResponseApi {
  message: string;
  results: AnalysisResult[];
}

export interface ResumeFileResponse {
  pdf_url: string;
}

export interface UploadContext {
  resumeNames: Record<string, string>;
  jdName?: string;
  uploadedAt: string;
}