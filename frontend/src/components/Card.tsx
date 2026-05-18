import type { ReactNode } from "react";

interface CardProps {
  title: string;
  value: ReactNode;
  hint?: string;
  tone?: "neutral" | "success" | "warning" | "danger";
}

const TONES: Record<NonNullable<CardProps["tone"]>, string> = {
  neutral: "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700",
  success: "bg-emerald-50 dark:bg-emerald-950 border-emerald-200 dark:border-emerald-800",
  warning: "bg-amber-50 dark:bg-amber-950 border-amber-200 dark:border-amber-800",
  danger: "bg-rose-50 dark:bg-rose-950 border-rose-200 dark:border-rose-800",
};

const VALUE_TONES: Record<NonNullable<CardProps["tone"]>, string> = {
  neutral: "text-slate-900 dark:text-slate-100",
  success: "text-emerald-800 dark:text-emerald-200",
  warning: "text-amber-800 dark:text-amber-200",
  danger: "text-rose-800 dark:text-rose-200",
};

export default function Card({ title, value, hint, tone = "neutral" }: CardProps) {
  return (
    <article className={`border rounded-lg p-4 shadow-sm ${TONES[tone]}`}>
      <h2 className="text-sm font-medium text-slate-600 dark:text-slate-400">{title}</h2>
      <p className={`mt-2 text-3xl font-bold ${VALUE_TONES[tone]}`}>{value}</p>
      {hint && <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{hint}</p>}
    </article>
  );
}
