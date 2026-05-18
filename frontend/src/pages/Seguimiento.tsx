import { useEffect, useState } from "react";
import { api, errorMessage } from "../lib/api";
import type { EstadoSeguimiento, SeguimientoMensual } from "../types";

const BADGE: Record<EstadoSeguimiento, string> = {
  Cumple: "bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200",
  En_mora: "bg-rose-100 dark:bg-rose-900 text-rose-800 dark:text-rose-200",
  Pendiente: "bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200",
};

export default function Seguimiento() {
  const hoy = new Date();
  const [anio, setAnio] = useState<number>(hoy.getFullYear());
  const [mes, setMes] = useState<number>(hoy.getMonth() + 1);
  const [rows, setRows] = useState<SeguimientoMensual[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.get<SeguimientoMensual[]>("/seguimiento", { params: { anio, mes } })
      .then((r) => setRows(r.data))
      .catch((e) => setError(errorMessage(e, "Error cargando seguimiento")))
      .finally(() => setLoading(false));
  }, [anio, mes]);

  return (
    <div>
      <header className="mb-4">
        <h1 className="text-2xl font-bold">Seguimiento mensual</h1>
        <p className="text-sm text-slate-600 dark:text-slate-400">Estado de pago SS y Nómina por empresa</p>
      </header>

      <fieldset className="mb-4 flex flex-wrap items-end gap-3">
        <legend className="sr-only">Filtros de período</legend>
        <label className="text-sm">
          <span className="block font-medium text-slate-700 dark:text-slate-300">Año</span>
          <input
            type="number"
            value={anio}
            min={2020}
            max={2100}
            onChange={(e) => setAnio(Number(e.target.value))}
            className="mt-1 w-24 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800"
          />
        </label>
        <label className="text-sm">
          <span className="block font-medium text-slate-700 dark:text-slate-300">Mes</span>
          <select
            value={mes}
            onChange={(e) => setMes(Number(e.target.value))}
            className="mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </label>
      </fieldset>

      {loading && <p role="status">Cargando…</p>}
      {error && <p role="alert" className="text-rose-700 dark:text-rose-300">{error}</p>}

      {!loading && !error && (
        <div className="overflow-x-auto bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
            <caption className="sr-only">Seguimiento mensual</caption>
            <thead className="bg-slate-50 dark:bg-slate-900/40">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Empresa</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">SS</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Plazo SS</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Pago SS</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Días mora</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Nómina</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {rows.map((s) => (
                <tr key={`${s.nit9}-${s.anio}-${s.mes}`}>
                  <td className="px-4 py-3">
                    <div className="font-medium">{s.nombre_empresa ?? s.nit9}</div>
                    <div className="text-xs font-mono text-slate-500 dark:text-slate-400">{s.nit9}</div>
                  </td>
                  <td className="px-4 py-3">
                    {s.ss_estado && <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${BADGE[s.ss_estado]}`}>{s.ss_estado.replace("_", " ")}</span>}
                  </td>
                  <td className="px-4 py-3 text-sm">{s.ss_fecha_plazo ?? "—"}</td>
                  <td className="px-4 py-3 text-sm">{s.ss_fecha_pago ?? "—"}</td>
                  <td className="px-4 py-3 text-sm text-right">{s.ss_dias_mora ?? "—"}</td>
                  <td className="px-4 py-3">
                    {s.nomina_estado && <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${BADGE[s.nomina_estado]}`}>{s.nomina_estado.replace("_", " ")}</span>}
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-500">Sin registros para este período</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
