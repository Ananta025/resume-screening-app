import Link from "next/link";

const links = [
  { href: "/", label: "Home" },
  { href: "/screening", label: "Screening" },
  { href: "/results", label: "Results" },
];

export function Sidebar() {
  return (
    <aside className="rounded-[1.75rem] border border-slate-200 bg-white/85 p-5 shadow-[0_20px_45px_rgba(15,23,42,0.08)] backdrop-blur">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">Navigation</p>
          <h2 className="mt-2 text-lg font-semibold text-slate-950">Pipeline hub</h2>
        </div>
        <div className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">Active</div>
      </div>

      <div className="mt-6 space-y-2">
        {links.map((link) => (
          <Link key={link.href} href={link.href} className="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50">
            <span>{link.label}</span>
            <span className="text-slate-400">↗</span>
          </Link>
        ))}
      </div>

      <div className="mt-6 rounded-3xl bg-slate-950 p-5 text-white">
        <p className="text-sm font-semibold">Deployment ready</p>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          API calls are isolated in the service layer, so a FastAPI backend can plug in later without changing the UI.
        </p>
      </div>
    </aside>
  );
}