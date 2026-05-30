interface LoadingOverlayProps {
  label?: string;
}

export function LoadingOverlay({ label = "Analyzing candidates..." }: LoadingOverlayProps) {
  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center rounded-[2rem] bg-white/70 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4 rounded-[1.5rem] border border-slate-200 bg-white px-6 py-5 shadow-xl">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-950" />
        <p className="text-sm font-medium text-slate-700">{label}</p>
      </div>
    </div>
  );
}