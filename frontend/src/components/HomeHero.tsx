import Link from "next/link";

export function HomeHero() {
  return (
    <main className="mx-auto flex w-full max-w-7xl flex-1 items-center px-4 py-10 sm:px-6 lg:px-8 lg:py-16">
      <section className="grid w-full gap-8 overflow-hidden rounded-[2rem] border border-white/70 bg-white/80 p-6 shadow-[0_30px_80px_rgba(15,23,42,0.12)] backdrop-blur md:p-10 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="flex flex-col justify-center gap-6">
          <div className="inline-flex w-fit items-center rounded-full border border-slate-200 bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-slate-600">
            Resume Screening System
          </div>
          <div className="space-y-4">
            <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
              AI Resume Screening & Candidate Ranking System
            </h1>
            <p className="max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
              Screen bulk resumes, compare candidates against a job description, and surface the strongest matches in a clean HR SaaS dashboard.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link href="/screening" className="inline-flex h-12 items-center justify-center rounded-full bg-slate-950 px-6 text-sm font-semibold text-white transition hover:bg-slate-800">
              Start Screening
            </Link>
            <Link href="/results" className="inline-flex h-12 items-center justify-center rounded-full border border-slate-300 px-6 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-100">
              View Results
            </Link>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {[
              ["Fast analysis", "Live backend-powered scoring"],
              ["Bulk uploads", "Multiple PDF, DOC, and DOCX files"],
              ["Actionable ranking", "Scores, skill gaps, and summaries"],
            ].map(([title, description]) => (
              <div key={title} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">{title}</p>
                <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="relative overflow-hidden rounded-[1.75rem] border border-slate-200 bg-slate-950 p-6 text-white shadow-2xl">
          <div className="absolute inset-x-0 top-0 h-40 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.35),_transparent_65%)]" />
          <div className="relative space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Live workspace</p>
                <h2 className="mt-2 text-2xl font-semibold">Candidate insights</h2>
              </div>
              <div className="rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-slate-200">
                Backend connected
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {[
                ["92%", "Top match score"],
                ["12", "Skills evaluated"],
                ["8", "Resumes processed"],
                ["3.2 yrs", "Average experience"],
              ].map(([value, label]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-3xl font-semibold">{value}</p>
                  <p className="mt-2 text-sm text-slate-300">{label}</p>
                </div>
              ))}
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <div className="flex items-center justify-between text-sm text-slate-300">
                <span>Ranking pipeline</span>
                <span>Ready for FastAPI</span>
              </div>
              <div className="mt-4 h-2 rounded-full bg-white/10">
                <div className="h-2 w-[78%] rounded-full bg-gradient-to-r from-cyan-400 via-sky-400 to-emerald-400" />
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                The frontend now streams uploads, analysis, and ranked results directly from the FastAPI backend.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}