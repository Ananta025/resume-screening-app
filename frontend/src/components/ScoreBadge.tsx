import { cn, formatScore } from "@/lib/utils";

interface ScoreBadgeProps {
  score: number;
}

export function ScoreBadge({ score }: ScoreBadgeProps) {
  const tone =
    score >= 90
      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
      : score >= 80
        ? "bg-sky-50 text-sky-700 border-sky-200"
        : score >= 70
          ? "bg-amber-50 text-amber-700 border-amber-200"
          : "bg-rose-50 text-rose-700 border-rose-200";

  return <span className={cn("inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold", tone)}>{formatScore(score)}</span>;
}