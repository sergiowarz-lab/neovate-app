import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errorMessage } from "../lib/api";
import type { DashboardKPIs } from "../types";
import Card from "../components/Card";

const MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

export default function Dashboard() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<DashboardKPIs>("/seguimiento/kpis")
      .then((r) => setKpis(r.data))
      .catch((e) => setError(errorMessage(e, "No se pudieron cargar los KPIs")))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        {kpis && (
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Período: {MESES[kpis.periodo_mes]} {kpis.periodo_anio}
          </p>
        )}
      </header>

      {loading && <p role="status" aria-live="polite" className="text-slate-600 dark:text-slate-400">Cargando KPIs…</p>}

      {error && (
        <p role="alert" className="text-sm text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950 border border-rose-200 dark:border-rose-800 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      {kpis && (
        <>
          <section aria-label="Indicadores clave" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card title="Empresas seguidas" value={kpis.total_empresas} tone="neutral" />
            <Card title="Cumple" value={kpis.cumple} tone="success" hint="Pagaron antes de la fecha límite" />
            <Card title="En mora" value={kpis.en_mora} tone="danger" hint="Pago vencido sin registrar" />
            <Card title="Pendiente" value={kpis.pendiente} tone="warning" hint="Plazo todavía vigente" />
          </section>

          <section aria-label="Accesos rápidos" className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Link to="/empresas" className="block p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-brand-500 transition-colors">
              <h2 className="font-semibold">Empresas</h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">Listado y detalle por NIT</p>
            </Link>
            <Link to="/historial" className="block p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-brand-500 transition-colors">
              <h2 className="font-semibold">Historial</h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">Reportes SS y Nómina</p>
            </Link>
            <Link to="/seguimiento" className="block p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-brand-500 transition-colors">
              <h2 className="font-semibold">Seguimiento mensual</h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">Cumple / Mora / Pendiente</p>
            </Link>
          </section>
        </>
      )}
    </div>
  );
}
