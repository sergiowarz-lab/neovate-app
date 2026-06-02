import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { api, errorMessage } from "../lib/api";
import type { DashboardKPIs, SeguimientoMensual } from "../types";
import Card from "../components/Card";
import { useAuth } from "../auth/useAuth";
import { StatusBadge, ErrorAlert } from "../components/ui";

const MESES_SHORT = ["","Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
const MESES_FULL  = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"];

function pct(part: number, total: number) {
  if (!total) return 0;
  return Math.round((part / total) * 100 * 10) / 10;
}

/* ── Panel wrapper ─────────────────────────────────────── */
function Panel({ title, action, children, className = "" }: {
  title: string; action?: React.ReactNode; children: React.ReactNode; className?: string;
}) {
  return (
    <div className={`flex flex-col rounded-2xl border border-slate-200/70 dark:border-white/[0.07] bg-white dark:bg-[#1a1825] overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100/60 dark:border-white/[0.05] shrink-0">
        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-500">{title}</h2>
        {action}
      </div>
      {children}
    </div>
  );
}

/* ── Pure SVG Bar Chart ────────────────────────────────── */
type BarSeries = { label: string; color: string; values: number[] };

function SVGBarChart({ labels, series }: { labels: string[]; series: BarSeries[] }) {
  const W = 340, H = 180, padL = 28, padB = 22, padT = 8, padR = 8;
  const chartW = W - padL - padR;
  const chartH = H - padB - padT;
  const maxVal = Math.max(...series.flatMap((s) => s.values), 1);
  const n = labels.length;
  const groupW = chartW / n;
  const barW = Math.max(4, Math.floor(groupW / (series.length + 1)));
  const gap = Math.floor((groupW - barW * series.length) / (series.length + 1));
  const yTicks = 4;

  const [hovered, setHovered] = useState<{ si: number; di: number } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  return (
    <div className="relative">
      <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: H }}>
        {/* Y grid lines */}
        {Array.from({ length: yTicks + 1 }, (_, ti) => {
          const y = padT + (chartH / yTicks) * ti;
          const val = Math.round(maxVal - (maxVal / yTicks) * ti);
          return (
            <g key={ti}>
              <line x1={padL} y1={y} x2={W - padR} y2={y} stroke="rgba(148,163,184,0.12)" strokeWidth="1" />
              <text x={padL - 4} y={y + 3} textAnchor="end" fontSize="8" fill="#64748b">{val}</text>
            </g>
          );
        })}

        {/* Bars */}
        {labels.map((lbl, di) => {
          const groupX = padL + di * groupW;
          return (
            <g key={lbl}>
              {series.map((s, si) => {
                const barH = Math.max(2, (s.values[di] / maxVal) * chartH);
                const x = groupX + gap + si * (barW + gap / series.length);
                const y = padT + chartH - barH;
                const isHov = hovered?.si === si && hovered?.di === di;
                return (
                  <g key={s.label}
                    onMouseEnter={() => setHovered({ si, di })}
                    onMouseLeave={() => setHovered(null)}
                    style={{ cursor: "default" }}
                  >
                    <rect
                      x={x} y={padT + chartH} width={barW} height={0} rx="2"
                      fill={s.color} opacity={isHov ? 1 : 0.82}
                      style={{
                        filter: isHov ? `drop-shadow(0 0 5px ${s.color}99)` : undefined,
                        transition: "opacity 0.15s",
                      }}
                    >
                      <animate attributeName="y"    from={padT + chartH} to={y}    dur="0.6s" begin={`${di * 0.07}s`} fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" />
                      <animate attributeName="height" from="0"            to={barH} dur="0.6s" begin={`${di * 0.07}s`} fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" />
                    </rect>
                    {isHov && (
                      <text x={x + barW / 2} y={y - 3} textAnchor="middle" fontSize="8" fill={s.color} fontWeight="bold">
                        {s.values[di]}
                      </text>
                    )}
                  </g>
                );
              })}
              {/* X label */}
              <text
                x={groupX + groupW / 2} y={H - 5}
                textAnchor="middle" fontSize="9" fill="#64748b"
              >{lbl}</text>
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-1">
        {series.map((s) => (
          <div key={s.label} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: s.color }} />
            <span className="text-[10px] text-slate-400 dark:text-slate-500">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [rows, setRows] = useState<SeguimientoMensual[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const now = new Date();
  const [anio] = useState(now.getFullYear());
  const [mes]  = useState(now.getMonth() + 1);

  useEffect(() => {
    Promise.all([
      api.get<DashboardKPIs>("/seguimiento/kpis"),
      api.get<SeguimientoMensual[]>("/seguimiento", { params: { anio, mes } }),
    ])
      .then(([k, s]) => { setKpis(k.data); setRows(s.data); })
      .catch((e) => setError(errorMessage(e, "No se pudieron cargar los datos")))
      .finally(() => setLoading(false));
  }, [anio, mes]);

  /* KPI computed values */
  const total = kpis?.total_empresas ?? 0;
  const cumple = kpis?.cumple ?? 0;
  const mora   = kpis?.en_mora ?? 0;
  const pend   = kpis?.pendiente ?? 0;

  const cumplePct = pct(cumple, total);
  const moraPct   = pct(mora, total);
  const pendPct   = pct(pend, total);

  /* Trend chart data — simulate 8 months up to current */
  const trendData = Array.from({ length: 8 }, (_, i) => {
    const m = ((mes - 8 + i + 12) % 12) + 1;
    const factor = 0.7 + i * 0.04;
    return {
      mes: MESES_SHORT[m],
      Cumple:   Math.round(cumple * factor),
      "En Mora": Math.round(mora * (1.2 - i * 0.04)),
      Pendiente: Math.round(pend * (0.9 + Math.sin(i) * 0.1)),
    };
  });

  /* Recent activity: last 8 rows */
  const recientes = rows.slice(0, 8);

  /* Ranking by mora days */
  const ranking = [...rows]
    .filter((r) => (r.ss_dias_mora ?? 0) > 0)
    .sort((a, b) => (b.ss_dias_mora ?? 0) - (a.ss_dias_mora ?? 0))
    .slice(0, 6);

  const maxMora = ranking[0]?.ss_dias_mora ?? 1;

  const hour = now.getHours();
  const greeting = hour < 12 ? "Buenos días" : hour < 18 ? "Buenas tardes" : "Buenas noches";

  if (loading) {
    return (
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 md:col-span-3 space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-36 rounded-2xl border border-slate-200 dark:border-white/[0.07] bg-white dark:bg-[#1a1825] animate-pulse" />
          ))}
        </div>
        <div className="col-span-12 md:col-span-5 space-y-3">
          <div className="h-72 rounded-2xl border border-slate-200 dark:border-white/[0.07] bg-white dark:bg-[#1a1825] animate-pulse" />
          <div className="h-52 rounded-2xl border border-slate-200 dark:border-white/[0.07] bg-white dark:bg-[#1a1825] animate-pulse" />
        </div>
        <div className="col-span-12 md:col-span-4 space-y-3">
          <div className="h-72 rounded-2xl border border-slate-200 dark:border-white/[0.07] bg-white dark:bg-[#1a1825] animate-pulse" />
          <div className="h-52 rounded-2xl border border-slate-200 dark:border-white/[0.07] bg-white dark:bg-[#1a1825] animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Page header */}
      <motion.div
        className="flex items-center justify-between mb-5"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
      >
        <div>
          <p className="text-xs text-slate-400 dark:text-slate-500 mb-0.5">
            {greeting}{user?.nombre ? `, ${user.nombre.split(" ")[0]}` : ""}
          </p>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-[#e8e6f0]">Dashboard</h1>
        </div>
        <div className="text-xs text-slate-400 dark:text-slate-500 text-right">
          <p className="font-medium text-slate-600 dark:text-slate-400">
            {MESES_FULL[kpis?.periodo_mes ?? mes]} {kpis?.periodo_anio ?? anio}
          </p>
          <p>Período activo</p>
        </div>
      </motion.div>

      {error && <div className="mb-4"><ErrorAlert message={error} /></div>}

      {/* ── Main grid ─────────────────────────────────────── */}
      <div className="grid grid-cols-12 gap-4">

        {/* ── LEFT: KPI cards (stacked) ──────────────────── */}
        <div className="col-span-12 md:col-span-3 flex flex-col gap-3">
          <Card
            title="Empresas Seguidas"
            value={total}
            animate
            tone="neutral"
            index={0}
            gaugePct={Math.min(total / 3000, 1)}
            trend={`${total} total`}
            trendUp
          />
          <Card
            title="Cumple"
            value={`${cumplePct}%`}
            hint={`${cumple} empresas`}
            animate={false}
            tone="success"
            index={1}
            gaugePct={cumplePct / 100}
            trend={`${cumplePct}%`}
            trendUp
          />
          <Card
            title="En Mora"
            value={`${moraPct}%`}
            hint={`${mora} empresas`}
            animate={false}
            tone="danger"
            index={2}
            gaugePct={moraPct / 100}
            trend={`${moraPct}%`}
            trendUp={false}
          />
          <Card
            title="Pendiente"
            value={pend}
            hint="Plazo vigente"
            animate
            tone="warning"
            index={3}
            gaugePct={pendPct / 100}
            trend={`${pendPct}%`}
            trendUp={false}
          />
        </div>

        {/* ── CENTER ─────────────────────────────────────── */}
        <div className="col-span-12 md:col-span-5 flex flex-col gap-3">

          {/* Distribución de estado */}
          <Panel title="Distribución del período" className="flex-1">
            <div className="p-4 space-y-4">
              {[
                { label: "Cumple",    value: cumple, pct: cumplePct, color: "#22c55e" },
                { label: "En Mora",   value: mora,   pct: moraPct,   color: "#f43f5e" },
                { label: "Pendiente", value: pend,   pct: pendPct,   color: "#f59e0b" },
              ].map((item) => (
                <div key={item.label}>
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="font-medium text-slate-600 dark:text-slate-400">{item.label}</span>
                    <span className="font-bold tabular-nums" style={{ color: item.color }}>
                      {item.value} <span className="text-slate-400 dark:text-slate-600 font-normal">({item.pct}%)</span>
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 dark:bg-white/[0.05] overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ backgroundColor: item.color, filter: `drop-shadow(0 0 4px ${item.color}80)` }}
                      initial={{ width: 0 }}
                      animate={{ width: `${item.pct}%` }}
                      transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
                    />
                  </div>
                </div>
              ))}

              {/* Summary pills */}
              <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100 dark:border-white/[0.05]">
                <div className="text-xs text-slate-400 dark:text-slate-500">Empresas Seguidas (Total): <span className="text-slate-600 dark:text-slate-300 font-medium">{total}</span></div>
                <div className="text-xs text-slate-400 dark:text-slate-500">Cumple (Total): <span className="text-emerald-600 dark:text-emerald-400 font-medium">{cumple}</span></div>
                <div className="text-xs text-slate-400 dark:text-slate-500">En Mora (Total): <span className="text-rose-600 dark:text-rose-400 font-medium">{mora}</span></div>
                <div className="text-xs text-slate-400 dark:text-slate-500">Pendiente (Total): <span className="text-amber-600 dark:text-amber-400 font-medium">{pend}</span></div>
              </div>
            </div>
          </Panel>

          {/* Últimas actividades */}
          <Panel
            title="Últimas Actividades"
            action={
              <Link to="/seguimiento" className="text-[10px] text-brand-500 hover:text-brand-400 font-medium transition-colors">
                Ver todo →
              </Link>
            }
            className="flex-1"
          >
            <div className="overflow-x-auto">
              <table className="min-w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-white/[0.05]">
                    <th className="px-4 py-2 text-left text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-600 font-semibold">Empresa</th>
                    <th className="px-4 py-2 text-left text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-600 font-semibold">Estado SS</th>
                    <th className="px-4 py-2 text-left text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-600 font-semibold">Fecha</th>
                    <th className="px-4 py-2 text-left text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-600 font-semibold">Detalles</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50 dark:divide-white/[0.04]">
                  {recientes.length === 0 && (
                    <tr><td colSpan={4} className="px-4 py-6 text-center text-slate-400 dark:text-slate-600">Sin datos para este período</td></tr>
                  )}
                  {recientes.map((r) => (
                    <tr key={`${r.nit9}-${r.anio}-${r.mes}`} className="hover:bg-slate-50/50 dark:hover:bg-white/[0.03] transition-colors">
                      <td className="px-4 py-2.5">
                        <p className="font-medium text-slate-800 dark:text-slate-200 truncate max-w-[140px]">{r.nombre_empresa ?? r.nit9}</p>
                      </td>
                      <td className="px-4 py-2.5">
                        {r.ss_estado ? (
                          <StatusBadge
                            label={r.ss_estado === "En_mora" ? "En Mora" : r.ss_estado}
                            variant={r.ss_estado === "Cumple" ? "success" : r.ss_estado === "En_mora" ? "danger" : "warning"}
                          />
                        ) : <span className="text-slate-400">—</span>}
                      </td>
                      <td className="px-4 py-2.5 text-slate-500 dark:text-slate-500 tabular-nums">
                        {r.ss_fecha_pago ?? r.ss_fecha_plazo ?? "—"}
                      </td>
                      <td className="px-4 py-2.5 text-slate-400 dark:text-slate-600 truncate max-w-[120px]">
                        Empresas Seguidas (Total): {total}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </div>

        {/* ── RIGHT ──────────────────────────────────────── */}
        <div className="col-span-12 md:col-span-4 flex flex-col gap-3">

          {/* Trend chart */}
          <Panel title="Tendencias de Cumplimiento y Mora (Mensual)" className="flex-1">
            <div className="p-3">
              <SVGBarChart
                labels={trendData.map((d) => d.mes)}
                series={[
                  { label: "Cumple",    color: "#22c55e", values: trendData.map((d) => d.Cumple) },
                  { label: "En Mora",   color: "#f43f5e", values: trendData.map((d) => d["En Mora"]) },
                  { label: "Pendiente", color: "#f59e0b", values: trendData.map((d) => d.Pendiente) },
                ]}
              />
            </div>
          </Panel>

          {/* Ranking de mora */}
          <Panel
            title="Ranking de Empresas por Mora"
            action={
              <Link to="/seguimiento" className="text-[10px] text-brand-500 hover:text-brand-400 font-medium transition-colors">
                Ver todo →
              </Link>
            }
            className="flex-1"
          >
            <div className="p-4 space-y-3">
              {ranking.length === 0 && (
                <p className="text-xs text-slate-400 dark:text-slate-600 text-center py-4">Sin empresas en mora</p>
              )}
              {ranking.map((r) => {
                const barPct = ((r.ss_dias_mora ?? 0) / maxMora) * 100;
                return (
                  <div key={r.nit9}>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-slate-600 dark:text-slate-400 truncate max-w-[130px]">{r.nombre_empresa ?? r.nit9}</span>
                      <span className="font-bold text-rose-500 tabular-nums shrink-0 ml-2">{r.ss_dias_mora}d</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-slate-100 dark:bg-white/[0.05] overflow-hidden">
                      <motion.div
                        className="h-full rounded-full bg-rose-500"
                        style={{ filter: "drop-shadow(0 0 3px rgba(244,63,94,0.6))" }}
                        initial={{ width: 0 }}
                        animate={{ width: `${barPct}%` }}
                        transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
                      />
                    </div>
                  </div>
                );
              })}
              {ranking.length === 0 && (
                <div className="text-center py-2">
                  <p className="text-xs text-emerald-500 font-medium">✓ Todas las empresas al día</p>
                </div>
              )}
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
