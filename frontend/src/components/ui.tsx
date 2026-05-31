import { useEffect, useState, type ReactNode, type InputHTMLAttributes, type SelectHTMLAttributes } from "react";
import { motion } from "motion/react";

// ─── Glass Panel ────────────────────────────────────────────────────────────

interface GlassPanelProps {
  children: ReactNode;
  className?: string;
  as?: "div" | "section" | "article" | "form";
  onSubmit?: (e: React.FormEvent) => void;
}

export function GlassPanel({ children, className = "", as: Tag = "div", onSubmit }: GlassPanelProps) {
  return (
    <Tag
      onSubmit={onSubmit}
      className={`bg-white dark:bg-white/5 backdrop-blur-sm border border-slate-200 dark:border-white/10 rounded-2xl shadow-sm ${className}`}
    >
      {children}
    </Tag>
  );
}

// ─── Page Header ─────────────────────────────────────────────────────────────

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export function PageHeader({ title, subtitle, action }: PageHeaderProps) {
  return (
    <motion.header
      className="mb-6 flex items-start justify-between gap-4"
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{title}</h1>
        {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </motion.header>
  );
}

// ─── Glass Input ─────────────────────────────────────────────────────────────

type GlassInputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  id: string;
  hint?: string;
};

export function GlassInput({ label, id, hint, className = "", ...props }: GlassInputProps) {
  return (
    <div>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          {label}
        </label>
      )}
      <input
        id={id}
        {...props}
        className={`w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 transition-colors ${className}`}
      />
      {hint && <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{hint}</p>}
    </div>
  );
}

// ─── Glass Select ─────────────────────────────────────────────────────────────

type GlassSelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
  id: string;
};

export function GlassSelect({ label, id, children, className = "", ...props }: GlassSelectProps) {
  return (
    <div>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          {label}
        </label>
      )}
      <select
        id={id}
        {...props}
        className={`w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-slate-100 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 transition-colors ${className}`}
      >
        {children}
      </select>
    </div>
  );
}

// ─── Glass Button ─────────────────────────────────────────────────────────────

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  children: ReactNode;
}

const BTN_VARIANT: Record<NonNullable<GlassButtonProps["variant"]>, string> = {
  primary:   "bg-brand-600 hover:bg-brand-500 active:bg-brand-700 text-white shadow-lg shadow-brand-600/30 disabled:opacity-60",
  secondary: "border border-slate-300 dark:border-white/10 bg-white dark:bg-white/5 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/10",
  danger:    "bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/20 disabled:opacity-60",
  ghost:     "text-brand-700 dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-500/10",
};

const BTN_SIZE: Record<NonNullable<GlassButtonProps["size"]>, string> = {
  sm: "px-3 py-1.5 text-xs rounded-lg",
  md: "px-4 py-2.5 text-sm rounded-xl",
  lg: "px-6 py-3 text-sm rounded-xl",
};

export function GlassButton({ variant = "primary", size = "md", children, className = "", ...props }: GlassButtonProps) {
  return (
    <button
      {...props}
      className={`inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200 disabled:cursor-not-allowed cursor-pointer ${BTN_VARIANT[variant]} ${BTN_SIZE[size]} ${className}`}
    >
      {children}
    </button>
  );
}

// ─── Status Badge ─────────────────────────────────────────────────────────────

type BadgeVariant = "success" | "warning" | "danger" | "info" | "neutral";

interface StatusBadgeProps {
  label: string;
  variant: BadgeVariant;
  pulse?: boolean;
}

const BADGE_STYLES: Record<BadgeVariant, string> = {
  success: "bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/30 text-emerald-800 dark:text-emerald-300",
  warning: "bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/30 text-amber-800 dark:text-amber-300",
  danger:  "bg-rose-50 dark:bg-rose-500/10 border-rose-200 dark:border-rose-500/30 text-rose-800 dark:text-rose-300",
  info:    "bg-sky-50 dark:bg-sky-500/10 border-sky-200 dark:border-sky-500/30 text-sky-800 dark:text-sky-300",
  neutral: "bg-slate-100 dark:bg-white/5 border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300",
};

const DOT_STYLES: Record<BadgeVariant, string> = {
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  danger:  "bg-rose-500",
  info:    "bg-sky-500",
  neutral: "bg-slate-400",
};

export function StatusBadge({ label, variant, pulse = false }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${BADGE_STYLES[variant]}`}>
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${DOT_STYLES[variant]} ${pulse ? "animate-pulse" : ""}`} />
      {label}
    </span>
  );
}

// ─── Animated Number ──────────────────────────────────────────────────────────

export function AnimatedNumber({ value }: { value: number }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    let raf: number;
    const start = performance.now();
    const duration = 1000;
    const tick = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(eased * value));
      if (progress < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value]);

  return <>{display}</>;
}

// ─── Table Wrapper ────────────────────────────────────────────────────────────

export function TableWrapper({ children }: { children: ReactNode }) {
  return (
    <motion.div
      className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 backdrop-blur-sm shadow-sm"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

export function TableHead({ children }: { children: ReactNode }) {
  return (
    <thead className="bg-slate-50/80 dark:bg-white/5 border-b border-slate-200 dark:border-white/10">
      {children}
    </thead>
  );
}

export function Th({ children, right }: { children: ReactNode; right?: boolean }) {
  return (
    <th scope="col" className={`px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 whitespace-nowrap ${right ? "text-right" : "text-left"}`}>
      {children}
    </th>
  );
}

export function Td({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <td className={`px-4 py-3 ${className}`}>
      {children}
    </td>
  );
}

// ─── Alert / Status messages ──────────────────────────────────────────────────

export function ErrorAlert({ message }: { message: string }) {
  return (
    <motion.p
      role="alert"
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-sm text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-xl px-4 py-2.5"
    >
      {message}
    </motion.p>
  );
}

export function SuccessAlert({ message }: { message: string }) {
  return (
    <motion.p
      role="status"
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-sm text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl px-4 py-2.5"
    >
      {message}
    </motion.p>
  );
}

export function InfoAlert({ message }: { message: string }) {
  return (
    <p role="status" className="text-sm text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl px-4 py-2.5">
      {message}
    </p>
  );
}

export function LoadingRow({ cols }: { cols: number }) {
  return (
    <tr>
      <td colSpan={cols} className="px-4 py-10 text-center text-slate-400 dark:text-slate-500 text-sm">
        <span role="status" aria-live="polite">Cargando…</span>
      </td>
    </tr>
  );
}

export function EmptyRow({ cols, message = "Sin resultados" }: { cols: number; message?: string }) {
  return (
    <tr>
      <td colSpan={cols} className="px-4 py-10 text-center text-slate-400 dark:text-slate-500 text-sm">
        {message}
      </td>
    </tr>
  );
}
