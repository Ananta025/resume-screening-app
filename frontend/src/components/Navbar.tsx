import Link from "next/link";

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/75 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-950 text-sm font-semibold text-white shadow-lg shadow-slate-950/20">
            RS
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-950">Resume Screening System</p>
            <p className="text-xs text-slate-500">Candidate ranking for HR teams</p>
          </div>
        </Link>
        <nav className="hidden items-center gap-2 md:flex">
          <Link className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-950" href="/">
            Home
          </Link>
          <Link className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-950" href="/screening">
            Screening
          </Link>
          <Link className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-950" href="/results">
            Results
          </Link>
        </nav>
        <Link href="/screening" className="inline-flex h-10 items-center justify-center rounded-full bg-slate-950 px-4 text-sm font-semibold text-white transition hover:bg-slate-800">
          Start Screening
        </Link>
      </div>
    </header>
  );
}