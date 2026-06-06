import { useEffect, useState, type FormEvent } from "react";
import { motion, AnimatePresence } from "motion/react";
import { api, errorMessage } from "../lib/api";
import type { Rol, Usuario } from "../types";
import {
  PageHeader, GlassPanel, GlassInput, GlassSelect, GlassButton,
  TableWrapper, TableHead, Th, Td, StatusBadge,
  ErrorAlert, LoadingRow, EmptyRow,
} from "../components/ui";

export default function Usuarios() {
  const [rows, setRows] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  function reload() {
    setLoading(true);
    setError(null);
    api.get<Usuario[]>("/usuarios")
      .then((r) => setRows(r.data))
      .catch((e) => setError(errorMessage(e, "Error cargando usuarios")))
      .finally(() => setLoading(false));
  }

  useEffect(() => { reload(); }, []);

  async function toggleActive(u: Usuario) {
    try {
      await api.patch(`/usuarios/${u.username}`, { activo: !u.activo });
      reload();
    } catch (e) {
      alert(errorMessage(e));
    }
  }

  return (
    <div>
      <PageHeader
        title="Usuarios"
        subtitle={`${rows.length} usuario${rows.length !== 1 ? "s" : ""} registrado${rows.length !== 1 ? "s" : ""}`}
        action={
          <GlassButton
            variant={showForm ? "secondary" : "primary"}
            onClick={() => setShowForm((s) => !s)}
          >
            {showForm ? "Cancelar" : "+ Nuevo usuario"}
          </GlassButton>
        }
      />

      <AnimatePresence>
        {showForm && (
          <motion.div
            key="form"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="overflow-hidden mb-6"
          >
            <UsuarioForm onCreated={() => { setShowForm(false); reload(); }} />
          </motion.div>
        )}
      </AnimatePresence>

      {error && <div className="mb-4"><ErrorAlert message={error} /></div>}

      <TableWrapper>
        <table className="min-w-full">
          <caption className="sr-only">Lista de usuarios</caption>
          <TableHead>
            <tr>
              <Th>Usuario</Th>
              <Th>Nombre</Th>
              <Th>Rol</Th>
              <Th>NIT9</Th>
              <Th>Estado</Th>
              <Th right>Acciones</Th>
            </tr>
          </TableHead>
          <tbody className="divide-y divide-slate-100 dark:divide-white/5">
            {loading && <LoadingRow cols={6} />}
            {!loading && rows.length === 0 && <EmptyRow cols={6} />}
            {!loading && rows.map((u, i) => (
              <motion.tr
                key={u.username}
                className="hover:bg-slate-50/80 dark:hover:bg-white/5 transition-colors"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.25, delay: i * 0.04 }}
              >
                <Td className="font-mono text-sm font-medium text-slate-900 dark:text-white">{u.username}</Td>
                <Td>{u.nombre}</Td>
                <Td>
                  <StatusBadge
                    label={u.rol}
                    variant={ROL_VARIANT[u.rol] ?? "neutral"}
                  />
                </Td>
                <Td className="font-mono text-xs text-slate-400">{u.nit_empresa ?? "—"}</Td>
                <Td>
                  <StatusBadge
                    label={u.activo ? "Activo" : "Inactivo"}
                    variant={u.activo ? "success" : "neutral"}
                    pulse={u.activo}
                  />
                </Td>
                <Td className="text-right">
                  <GlassButton
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleActive(u)}
                    aria-label={u.activo ? `Desactivar ${u.username}` : `Activar ${u.username}`}
                  >
                    {u.activo ? "Desactivar" : "Activar"}
                  </GlassButton>
                </Td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </TableWrapper>
    </div>
  );
}

const ROL_VARIANT: Record<string, "warning" | "info" | "success" | "neutral"> = {
  admin: "warning", analista: "info", empresa: "success", viewer: "neutral",
};

function UsuarioForm({ onCreated }: { onCreated: () => void }) {
  const [form, setForm] = useState({
    username: "", nombre: "", email: "", password: "",
    rol: "viewer" as Rol, nit_empresa: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const needsNit = form.rol === "empresa";

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (needsNit && !form.nit_empresa) {
      setError("El rol 'empresa' requiere un NIT9 asociado");
      return;
    }
    setLoading(true);
    try {
      await api.post("/usuarios", {
        username:    form.username,
        nombre:      form.nombre,
        email:       form.email || null,
        password:    form.password,
        rol:         form.rol,
        nit_empresa: needsNit ? form.nit_empresa || null : null,
      });
      onCreated();
    } catch (err) {
      setError(errorMessage(err, "No se pudo crear el usuario"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <GlassPanel as="form" onSubmit={submit} className="p-6">
      <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">Nuevo usuario</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <GlassInput
          id="new-username"
          label="Usuario"
          required
          pattern="[a-zA-Z0-9_.\-]+"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
        />
        <GlassInput
          id="new-nombre"
          label="Nombre"
          required
          value={form.nombre}
          onChange={(e) => setForm({ ...form, nombre: e.target.value })}
        />
        <GlassInput
          id="new-email"
          label="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <GlassInput
          id="new-password"
          label="Contraseña inicial"
          type="password"
          required
          minLength={8}
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <GlassSelect
          id="new-rol"
          label="Rol"
          value={form.rol}
          onChange={(e) => setForm({ ...form, rol: e.target.value as Rol })}
        >
          <option value="viewer">viewer</option>
          <option value="analista">analista</option>
          <option value="empresa">empresa</option>
          <option value="admin">admin</option>
        </GlassSelect>
        {needsNit && (
          <GlassInput
            id="new-nit"
            label="NIT9 Empresa (9 dígitos)"
            required
            maxLength={9}
            pattern="\d{9}"
            value={form.nit_empresa}
            onChange={(e) => setForm({ ...form, nit_empresa: e.target.value })}
          />
        )}
      </div>

      <div className="mt-5 flex items-center gap-3">
        <GlassButton type="submit" disabled={loading}>
          {loading ? "Guardando…" : "Crear usuario"}
        </GlassButton>
        {error && <ErrorAlert message={error} />}
      </div>
    </GlassPanel>
  );
}
