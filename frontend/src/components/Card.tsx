import type { ReactNode } from "react";
import { motion } from "motion/react";
import { AnimatedNumber } from "./ui";
import { use3DTilt } from "../hooks/use3DTilt";

interface CardProps {
  title: string;
  value: ReactNode;
  hint?: string;
  tone?: "neutral" | "success" | "warning" | "danger";
  index?: number;
  animate?: boolean;
  /** 0–1, for the gauge arc fill */
  gaugePct?: number;
  /** e.g. "+12%" or "▲ 3" */
  trend?: string;
  trendUp?: boolean;
}

const BG: Record<NonNullable<CardProps["tone"]>, string> = {
  neutral: "bg-white dark:bg-[#1a1825] border-slate-200/80 dark:border-white/[0.07]",
  success: "bg-white dark:bg-[#1a1825] border-slate-200/80 dark:border-emerald-500/20",
  warning: "bg-white dark:bg-[#1a1825] border-slate-200/80 dark:border-amber-500/20",
  danger:  "bg-white dark:bg-[#1a1825] border-slate-200/80 dark:border-rose-500/20",
};

const VALUE_COLOR: Record<NonNullable<CardProps["tone"]>, string> = {
  neutral: "text-slate-900 dark:text-brand-400",
  success: "text-emerald-700 dark:text-emerald-400",
  warning: "text-amber-700 dark:text-amber-400",
  danger:  "text-rose-700 dark:text-rose-400",
};

const VALUE_GLOW: Record<NonNullable<CardProps["tone"]>, string> = {
  neutral: "value-glow-gold",
  success: "value-glow-emerald",
  warning: "value-glow-amber",
  danger:  "value-glow-rose",
};

const TOP_LINE: Record<NonNullable<CardProps["tone"]>, string> = {
  neutral: "from-brand-400 via-brand-300 to-brand-500",
  success: "from-emerald-400 via-emerald-300 to-teal-400",
  warning: "from-amber-400 via-yellow-300 to-amber-500",
  danger:  "from-rose-400 via-red-300 to-rose-500",
};

const GAUGE_COLOR: Record<NonNullable<CardProps["tone"]>, string> = {
  neutral: "#c9a84c",
  success: "#22c55e",
  warning: "#f59e0b",
  danger:  "#f43f5e",
};

const HOVER_GLOW: Record<NonNullable<CardProps["tone"]>, string> = {
  neutral: "hover:shadow-[0_8px_40px_rgba(201,168,76,0.18)] dark:hover:shadow-[0_8px_50px_rgba(201,168,76,0.15)]",
  success: "hover:shadow-[0_8px_40px_rgba(34,197,94,0.15)] dark:hover:shadow-[0_8px_50px_rgba(34,197,94,0.13)]",
  warning: "hover:shadow-[0_8px_40px_rgba(245,158,11,0.15)] dark:hover:shadow-[0_8px_50px_rgba(245,158,11,0.13)]",
  danger:  "hover:shadow-[0_8px_40px_rgba(244,63,94,0.15)] dark:hover:shadow-[0_8px_50px_rgba(244,63,94,0.13)]",
};

/* ── SVG Gauge ──────────────────────────────────────────── */
function GaugeArc({ pct, color }: { pct: number; color: string }) {
  const r  = 38;
  const cx = 50;
  const cy = 52;
  const arc = Math.PI * r; // ≈ 119.4

  const clampedPct = Math.max(0, Math.min(1, pct));
  const offset = arc * (1 - clampedPct);

  const d = `M ${cx - r} ${cy} A ${r} ${r} 0 0 0 ${cx + r} ${cy}`;

  return (
    <svg viewBox="0 0 100 58" className="w-[110px] shrink-0" aria-hidden="true">
      <path d={d} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="7" strokeLinecap="round" />
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth="7"
        strokeLinecap="round"
        strokeDasharray={`${arc}`}
        strokeDashoffset={`${offset}`}
        className="gauge-stroke"
        style={{ filter: `drop-shadow(0 0 5px ${color}99)` }}
      />
      {/* Center dot */}
      <circle cx={cx} cy={cy} r="3" fill={color} style={{ filter: `drop-shadow(0 0 4px ${color})` }} />
    </svg>
  );
}

/* ── SVG Sparkline ──────────────────────────────────────── */
function Sparkline({ seed, color }: { seed: number; color: string }) {
  const points = Array.from({ length: 20 }, (_, i) => {
    return 0.5 + Math.sin(i * 0.6 + seed) * 0.28 + Math.cos(i * 1.1 + seed * 0.13) * 0.18;
  });
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = max - min || 0.01;
  const W = 200;
  const H = 28;
  const norm = points.map((p) => (p - min) / range);
  const pathD = norm.map((y, i) => `${i === 0 ? "M" : "L"} ${(i / (points.length - 1)) * W} ${H - y * H}`).join(" ");
  const areaD = `${pathD} L ${W} ${H} L 0 ${H} Z`;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 28 }} preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id={`sg-${seed}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.28" />
          <stop offset="100%" stopColor={color} stopOpacity="0.01" />
        </linearGradient>
      </defs>
      <path d={areaD} fill={`url(#sg-${seed})`} />
      <path d={pathD} fill="none" stroke={color} strokeWidth="1.5"
        style={{ filter: `drop-shadow(0 1px 4px ${color}80)` }} />
    </svg>
  );
}

export default function Card({
  title, value, hint, tone = "neutral", index = 0, animate = true, gaugePct = 0.5, trend, trendUp,
}: CardProps) {
  const numericValue = typeof value === "number" ? value : null;
  const tilt = use3DTilt(8);
  const color = GAUGE_COLOR[tone];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: "easeOut" }}
      style={{ perspective: "900px" }}
    >
      <div className="group/card relative h-full">
        <div className="absolute -inset-px rounded-2xl opacity-0 group-hover/card:opacity-100 transition-opacity duration-500 holo-border" />
        <div
          ref={tilt.ref}
          style={tilt.style}
          onMouseMove={tilt.onMouseMove}
          onMouseLeave={tilt.onMouseLeave}
          className="relative h-full"
        >
          <article className={`relative h-full border rounded-2xl overflow-hidden transition-all duration-300 ${BG[tone]} ${HOVER_GLOW[tone]}`}>
            {/* Top accent bar */}
            <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${TOP_LINE[tone]}`} />
            <div className="absolute top-0 left-0 right-0 h-16 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />

            {/* Card body */}
            <div className="p-4">
              <div className="flex items-start justify-between gap-2">
                {/* Left: title + value + trend */}
                <div className="flex-1 min-w-0">
                  <h2 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500">{title}</h2>
                  <p className={`mt-1.5 text-3xl font-bold tabular-nums leading-none ${VALUE_COLOR[tone]} ${VALUE_GLOW[tone]}`}>
                    {animate && numericValue !== null ? <AnimatedNumber value={numericValue} /> : value}
                  </p>
                  {trend && (
                    <p className={`mt-1 text-xs font-medium ${trendUp ? "text-emerald-500" : "text-rose-500"}`}>
                      {trendUp ? "▲" : "▼"} {trend}
                    </p>
                  )}
                  {hint && !trend && (
                    <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">{hint}</p>
                  )}
                </div>

                {/* Right: gauge */}
                <GaugeArc pct={gaugePct} color={color} />
              </div>
            </div>

            {/* Sparkline at bottom */}
            <div className="px-0 pb-0 mt-auto">
              <Sparkline seed={numericValue ?? index * 7} color={color} />
            </div>
          </article>
        </div>
      </div>
    </motion.div>
  );
}
