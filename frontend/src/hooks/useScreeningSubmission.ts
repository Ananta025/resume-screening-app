"use client";

import { useCallback, useState } from "react";
import { analyzeCandidateResumes } from "@/services/api";
import type { CandidateAnalysisResult } from "@/types/candidate";
import type { ScreeningRequest } from "@/types/job";
import { useToast } from "@/hooks/useToast";

export function useScreeningSubmission() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const submit = useCallback(async (request: ScreeningRequest): Promise<CandidateAnalysisResult> => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await analyzeCandidateResumes(request);
      toast.success("Analysis completed", "Candidates were uploaded and ranked successfully.");
      return response;
    } catch (exception) {
      const message = exception instanceof Error ? exception.message : "Unable to analyze candidates";
      setError(message);
      toast.error("Analysis failed", message);
      throw exception;
    } finally {
      setIsSubmitting(false);
    }
  }, [toast]);

  return {
    submit,
    isSubmitting,
    error,
  };
}