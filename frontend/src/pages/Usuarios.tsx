import { useEffect, useState, type FormEvent } from "react";
import { api, errorMessage } from "../lib/api";
import type { Rol, Usuario } from "../types";

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
      <header className="mb-4 flex items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Usuarios</h1>
        <button
          type="button"
          onClick={() => setShowForm((s) => !s)}
          className="px-3 py-2 rounded-md bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium"
        >
          {showForm ? "Cancelar" : "Nuevo usuario"}
        </button>
      </header>

      {showForm && <UsuarioForm onCreated={() => { setShowForm(false); reload(); }} />}

      {loading && <p role="status">Cargando…</p>}
      {error && <p role="alert" className="text-rose-700 dark:text-rose-300">{error}</p>}

      {!loading && !error && (
        <div className="overflow-x-auto bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
            <caption className="sr-only">Lista de usuarios</caption>
            <thead className="bg-slate-50 dark:bg-slate-900/40">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Usuario</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Nombre</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Rol</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase">Activo</th>
                <th scope="col" className="px-4 py-3 text-right text-xs font-semibold uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {rows.map((u) => (
                <tr key={u.username}>
                  <td className="px-4 py-3 font-mono text-sm">{u.username}</td>
                  <td className="px-4 py-3">{u.nombre}</td>
                  <td className="px-4 py-3 text-sm">{u.rol}</td>
                  <td className="px-4 py-3 text-sm">{u.activo ? "Sí" : "No"}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => toggleActive(u)}
                      className="text-sm text-brand-700 dark:text-brand-400 hover:underline"
                      aria-label={u.activo ? `Desactivar ${u.username}` : `Activar ${u.username}`}
                    >
                      {u.activo ? "Desactivar" : "Activar"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function UsuarioForm({ onCreated }: { onCreated: () => void }) {
  const [form, setForm] = useState({ username: "", nombre: "", email: "", password: "", rol: "viewer" as Rol });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.post("/usuarios", {
        username: form.username,
        nombre: form.nombre,
        email: form.email || null,
        password: form.password,
        rol: form.rol,
      });
      onCreated();
    } catch (err) {
      setError(errorMessage(err, "No se pudo crear el usuario"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-3 p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
      <label className="text-sm">
        <span className="block font-medium">Usuario</span>
        <input required pattern="[a-zA-Z0-9_.\-]+" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900" />
      </label>
      <label className="text-sm">
        <span className="block font-medium">Nombre</span>
        <input required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900" />
      </label>
      <label className="text-sm">
        <span className="block font-medium">Email</span>
        <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900" />
      </label>
      <label className="text-sm">
        <span className="block font-medium">Contraseña inicial</span>
        <input required minLength={8} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900" />
      </label>
      <label className="text-sm">
        <span className="block font-medium">Rol</span>
        <select value={form.rol} onChange={(e) => setForm({ ...form, rol: e.target.value as Rol })} className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900">
          <option value="viewer">viewer</option>
          <option value="admin">admin</option>
        </select>
      </label>
      <div className="md:col-span-2 flex items-center gap-3 mt-2">
        <button type="submit" disabled={loading} className="px-4 py-2 rounded-md bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium disabled:opacity-60">
          {loading ? "Guardando…" : "Crear"}
        </button>
        {error && <span role="alert" className="text-rose-700 dark:text-rose-300 text-sm">{error}</span>}
      </div>
    </form>
  );
}
