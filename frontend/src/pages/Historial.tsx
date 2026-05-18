import { useEffect, useState } from "react";
import { api, errorMessage } from "../lib/api";
import type { EstadoReporte, ReporteNomina, ReporteSS } from "../types";

type Tab = "ss" | "nomina";

const ESTADO_LABEL: Record<EstadoReporte, string> = {
  Validado_ok: "Validado",
  Rechazado: "Rechazado",
  Validado_individual: "Validado (individual)",
};

const ESTADO_BADGE: Record<EstadoReporte, string> = {
  Validado_ok: "bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200",
  Rechazado: "bg-rose-100 dark:bg-rose-900 text-rose-800 dark:text-rose-200",
  Validado_individual: "bg-sky-100 dark:bg-sky-900 text-sky-800 dark:text-sky-200",
};

export default function Historial() {
  const [tab, setTab] = useState<Tab>("ss");
  const [ss, setSS] = useState<ReporteSS[]>([]);
  const [nomina, setNomina] = useState<ReporteNomina[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const url = tab === "ss" ? "/reportes/ss" : "/reportes/nomina";
    api.get(url)
      .then((r) => {
        if (tab === "ss") setSS(r.data);
        else setNomina(r.data);
      })
      .catch((e) => setError(errorMessage(e, "Error cargando historial")))
      .finally(() => setLoading(false));
  }, [tab]);

  return (
    <div>
      <header className="mb-4">
        <h1 className="text-2xl font-bold">Historial</h1>
      </header>

      <div role="tablist" aria-label="Tipo de reporte" className="inline-flex rounded-md border border-slate-300 dark:border-slate-600 overflow-hidden mb-4">
        {(["ss", "nomina"] as const).map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium ${
              tab === t
                ? "bg-brand-600 text-white"
                : "bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
            }`}
          >
            {t === "ss" ? "Seguridad Social" : "Nómina"}
          </button>
        ))}
      </div>

      {loading && <p role="status">Cargando…</p>}
      {error && <p role="alert" className="text-rose-700 dark:text-rose-300">{error}</p>}

      {!loading && !error && tab === "ss" && (
        <ReportTable rows={ss} type="ss" />
      )}
      {!loading && !error && tab === "nomina" && (
        <ReportTable rows={nomina} type="nomina" />
      )}
    </div>
  );
}

function ReportTable({
  rows,
  type,
}: {
  rows: (ReporteSS | ReporteNomina)[];
  type: "ss" | "nomina";
}) {
  return (
    <div className="overflow-x-auto bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
      <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
        <caption className="sr-only">Historial de reportes de {type === "ss" ? "Seguridad Social" : "Nómina"}</caption>
        <thead className="bg-slate-50 dark:bg-slate-900/40">
          <tr>
            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">ID</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">NIT</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Aliado</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Período</th>
            {type === "ss" && <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Operador</th>}
            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Estado</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Fecha pago</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
          {rows.map((r) => (
            <tr key={r.id}>
              <td className="px-4 py-3 font-mono text-xs">{r.id}</td>
              <td className="px-4 py-3 font-mono text-sm">{r.nit}</td>
              <td className="px-4 py-3">{r.aliado ?? "—"}</td>
              <td className="px-4 py-3 text-sm">{r.anio}-{String(r.mes_obligacion).padStart(2, "0")}</td>
              {type === "ss" && <td className="px-4 py-3 text-sm">{(r as ReporteSS).operador ?? "—"}</td>}
              <td className="px-4 py-3">
                <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${ESTADO_BADGE[r.estado]}`}>
                  {ESTADO_LABEL[r.estado]}
                </span>
              </td>
              <td className="px-4 py-3 text-sm">{r.fecha_pago ?? "—"}</td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr><td colSpan={type === "ss" ? 7 : 6} className="px-4 py-8 text-center text-slate-500">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
