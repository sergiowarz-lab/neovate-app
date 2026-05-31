import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { api, errorMessage } from "../lib/api";
import type { Empresa } from "../types";
import {
  PageHeader, GlassInput, TableWrapper, TableHead, Th, Td,
  StatusBadge, ErrorAlert, LoadingRow, EmptyRow,
} from "../components/ui";

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
      <PageHeader
        title="Empresas aliadas"
        subtitle={`${data.length} ${data.length === 1 ? "resultado" : "resultados"}`}
      />

      <motion.div
        className="flex flex-col sm:flex-row gap-3 mb-5"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.1 }}
      >
        <div className="flex-1">
          <label className="sr-only" htmlFor="search-empresa">Buscar empresa por NIT o nombre</label>
          <GlassInput
            id="search-empresa"
            type="search"
            placeholder="Buscar por NIT o nombre…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            aria-label="Buscar empresa por NIT o nombre"
          />
        </div>
        <label className="inline-flex items-center gap-2.5 text-sm text-slate-700 dark:text-slate-300 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 backdrop-blur-sm cursor-pointer hover:border-brand-500 transition-colors">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="w-4 h-4 rounded text-brand-600 border-slate-300 dark:border-white/20"
          />
          Mostrar inactivas
        </label>
      </motion.div>

      {error && <div className="mb-4"><ErrorAlert message={error} /></div>}

      <TableWrapper>
        <table className="min-w-full">
          <caption className="sr-only">Lista de empresas aliadas</caption>
          <TableHead>
            <tr>
              <Th>NIT</Th>
              <Th>NIT9</Th>
              <Th>Nombre</Th>
              <Th>Estado</Th>
            </tr>
          </TableHead>
          <tbody className="divide-y divide-slate-100 dark:divide-white/5">
            {loading && <LoadingRow cols={4} />}
            {!loading && data.length === 0 && <EmptyRow cols={4} />}
            {!loading && data.map((e, i) => (
              <motion.tr
                key={e.nit}
                className="hover:bg-slate-50/80 dark:hover:bg-white/5 transition-colors"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.25, delay: i * 0.03 }}
              >
                <Td className="font-mono text-sm font-medium text-slate-900 dark:text-white">{e.nit}</Td>
                <Td className="font-mono text-sm text-slate-500 dark:text-slate-400">{e.nit9}</Td>
                <Td className="font-medium">{e.nombre_empresa}</Td>
                <Td>
                  <StatusBadge
                    label={e.activa ? "Activa" : "Inactiva"}
                    variant={e.activa ? "success" : "neutral"}
                  />
                </Td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </TableWrapper>
    </div>
  );
}
