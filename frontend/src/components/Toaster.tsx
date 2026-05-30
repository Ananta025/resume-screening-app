"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

type ToastVariant = "success" | "error" | "info";

interface ToastItem {
  id: string;
  title: string;
  description?: string;
  variant: ToastVariant;
}

interface ToastInput {
  title: string;
  description?: string;
  variant?: ToastVariant;
}

interface ToastContextValue {
  notify: (toast: ToastInput) => void;
  success: (title: string, description?: string) => void;
  error: (title: string, description?: string) => void;
  info: (title: string, description?: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

function buildId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const notify = useCallback((toast: ToastInput) => {
    const nextToast: ToastItem = {
      id: buildId(),
      title: toast.title,
      description: toast.description,
      variant: toast.variant ?? "info",
    };

    setToasts((current) => [nextToast, ...current].slice(0, 4));

    window.setTimeout(() => removeToast(nextToast.id), 4000);
  }, [removeToast]);

  const value = useMemo<ToastContextValue>(
    () => ({
      notify,
      success: (title, description) => notify({ title, description, variant: "success" }),
      error: (title, description) => notify({ title, description, variant: "error" }),
      info: (title, description) => notify({ title, description, variant: "info" }),
    }),
    [notify],
  );

  useEffect(() => {
    return () => setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-20 z-[60] flex w-[min(92vw,24rem)] flex-col gap-3">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto rounded-2xl border bg-white p-4 shadow-[0_20px_50px_rgba(15,23,42,0.14)] ${
              toast.variant === "success"
                ? "border-emerald-200"
                : toast.variant === "error"
                  ? "border-rose-200"
                  : "border-slate-200"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-950">{toast.title}</p>
                {toast.description ? <p className="mt-1 text-sm leading-6 text-slate-600">{toast.description}</p> : null}
              </div>
              <button type="button" onClick={() => removeToast(toast.id)} className="text-sm font-semibold text-slate-400 transition hover:text-slate-800">
                ×
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }

  return context;
}