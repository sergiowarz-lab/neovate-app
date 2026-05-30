import { useEffect, useState } from "react";
import { api, errorMessage } from "../lib/api";
import type { Empresa } from "../types";

export default function Empresas() {
  const [data, setData] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [showInactive, setShowInactive] = useState(false);

  useEffect(() => {
    const params: Record<string, string | boolean> = {};
    if (q.trim()) params.q = q.trim();
    if (!showInactive) params.activa = true;

    setLoading(true);
    api.get<Empresa[]>("/empresas", { params })
      .then((r) => setData(r.data))
      .catch((e) => setError(errorMessage(e, "No se pudieron cargar empresas")))
      .finally(() => setLoading(false));
  }, [q, showInactive]);

  return (
    <div>
      <header className="mb-4">
        <h1 className="text-2xl font-bold">Empresas aliadas</h1>
        <p className="text-sm text-slate-600 dark:text-slate-400">{data.length} resultados</p>
      </header>

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <label className="flex-1">
          <span className="sr-only">Buscar empresa por NIT o nombre</span>
          <input
            type="search"
            placeholder="Buscar por NIT o nombre…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800"
            aria-label="Buscar empresa por NIT o nombre"
          />
        </label>
        <label className="inline-flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="w-4 h-4 text-brand-600 rounded"
          />
          Mostrar inactivas
        </label>
      </div>

      {loading && <p role="status" aria-live="polite">Cargando…</p>}
      {error && <p role="alert" className="text-rose-700 dark:text-rose-300">{error}</p>}

      {!loading && !error && (
        <div className="overflow-x-auto bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
            <caption className="sr-only">Lista de empresas aliadas</caption>
            <thead className="bg-slate-50 dark:bg-slate-900/40">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase whitespace-nowrap">NIT</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase whitespace-nowrap">NIT9</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase whitespace-nowrap">Nombre</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase whitespace-nowrap">Activa</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {data.map((e) => (
                <tr key={e.nit} className="hover:bg-slate-50 dark:hover:bg-slate-900/40">
                  <td className="px-4 py-3 font-mono text-sm">{e.nit}</td>
                  <td className="px-4 py-3 font-mono text-sm text-slate-600 dark:text-slate-400">{e.nit9}</td>
                  <td className="px-4 py-3">{e.nombre_empresa}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                        e.activa
                          ? "bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200"
                          : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      {e.activa ? "Sí" : "No"}
                    </span>
                  </td>
                </tr>
              ))}
              {data.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-slate-500">Sin resultados</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
