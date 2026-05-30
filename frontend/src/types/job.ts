export interface UploadedDocument {
  id: string;
  name: string;
  size: number;
  type: string;
  file?: File;
}

export interface JobDescriptionInput {
  description: string;
  file?: File;
  fileName?: string;
}

export interface ScreeningRequest {
  resumes: UploadedDocument[];
  jobDescription: JobDescriptionInput;
}