import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { api, errorMessage } from "../lib/api";
import type { EstadoReporte, ReporteNomina, ReporteSS } from "../types";
import {
  PageHeader, TableWrapper, TableHead, Th, Td,
  StatusBadge, ErrorAlert, LoadingRow, EmptyRow,
} from "../components/ui";

type Tab = "ss" | "nomina";

const ESTADO_LABEL: Record<EstadoReporte, string> = {
  Validado_ok:         "Validado",
  Rechazado:           "Rechazado",
  Validado_individual: "Ind.",
};

const ESTADO_VARIANT: Record<EstadoReporte, "success" | "danger" | "info"> = {
  Validado_ok:         "success",
  Rechazado:           "danger",
  Validado_individual: "info",
};

const TABS: { key: Tab; label: string }[] = [
  { key: "ss",     label: "Seguridad Social" },
  { key: "nomina", label: "Nómina" },
];

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

  const rows = tab === "ss" ? ss : nomina;

  return (
    <div>
      <PageHeader title="Historial de reportes" subtitle="Registros de Seguridad Social y Nómina" />

      <motion.div
        role="tablist"
        aria-label="Tipo de reporte"
        className="inline-flex gap-1 p-1 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 mb-5"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        {TABS.map((t) => (
          <button
            key={t.key}
            role="tab"
            aria-selected={tab === t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 cursor-pointer ${
              tab === t.key
                ? "bg-brand-600 text-white shadow-md shadow-brand-600/30"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            {t.label}
          </button>
        ))}
      </motion.div>

      {error && <div className="mb-4"><ErrorAlert message={error} /></div>}

      <TableWrapper>
        <table className="min-w-full">
          <caption className="sr-only">
            Historial de reportes de {tab === "ss" ? "Seguridad Social" : "Nómina"}
          </caption>
          <TableHead>
            <tr>
              <Th>ID</Th>
              <Th>NIT</Th>
              <Th>Aliado</Th>
              <Th>Período</Th>
              {tab === "ss" && <Th>Operador</Th>}
              <Th>Estado</Th>
              <Th>Fecha pago</Th>
            </tr>
          </TableHead>
          <tbody className="divide-y divide-slate-100 dark:divide-white/5">
            {loading && <LoadingRow cols={tab === "ss" ? 7 : 6} />}
            {!loading && rows.length === 0 && <EmptyRow cols={tab === "ss" ? 7 : 6} />}
            {!loading && rows.map((r, i) => (
              <motion.tr
                key={r.id}
                className="hover:bg-slate-50/80 dark:hover:bg-white/5 transition-colors"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2, delay: i * 0.02 }}
              >
                <Td className="font-mono text-xs text-slate-400 dark:text-slate-500">{r.id}</Td>
                <Td className="font-mono text-sm font-medium text-slate-900 dark:text-white">{r.nit}</Td>
                <Td className="text-sm">{r.aliado ?? "—"}</Td>
                <Td className="text-sm tabular-nums">
                  {r.anio}-{String(r.mes_obligacion).padStart(2, "0")}
                </Td>
                {tab === "ss" && <Td className="text-sm">{(r as ReporteSS).operador ?? "—"}</Td>}
                <Td>
                  <StatusBadge label={ESTADO_LABEL[r.estado]} variant={ESTADO_VARIANT[r.estado]} />
                </Td>
                <Td className="text-sm text-slate-600 dark:text-slate-400">{r.fecha_pago ?? "—"}</Td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </TableWrapper>
    </div>
  );
}
