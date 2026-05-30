"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchAnalysisResultById, fetchLatestAnalysis } from "@/services/api";
import type { Candidate, CandidateAnalysisResult } from "@/types/candidate";
import { useToast } from "@/hooks/useToast";

export function useAnalysisResults() {
  const [data, setData] = useState<CandidateAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const nextData = await fetchLatestAnalysis();
      setData(nextData);
      return nextData;
    } catch (exception) {
      const message = exception instanceof Error ? exception.message : "Failed to fetch analysis results";
      setError(message);
      toast.error("Failed to load results", message);
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    queueMicrotask(() => {
      void load();
    });
  }, [load]);

  const getById = useCallback(async (id: number): Promise<Candidate> => {
    return fetchAnalysisResultById(id);
  }, []);

  return {
    data,
    isLoading,
    error,
    refresh: load,
    getById,
  };
}