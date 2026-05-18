import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { useTheme } from "../theme/useTheme";
import { useState } from "react";

type NavItem = { to: string; label: string; end?: boolean };

const NAV: NavItem[] = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/empresas", label: "Empresas" },
  { to: "/historial", label: "Historial" },
  { to: "/seguimiento", label: "Seguimiento" },
];

const ADMIN_NAV: NavItem[] = [{ to: "/usuarios", label: "Usuarios" }];

export default function Layout() {
  const { user, logout } = useAuth();
  const { theme, toggle } = useTheme();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const items = [...NAV, ...(user?.rol === "admin" ? ADMIN_NAV : [])];

  return (
    <div className="min-h-full flex flex-col bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100">
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center h-16 gap-4">
          <Link to="/" className="flex items-center gap-2 font-semibold text-lg" aria-label="Inicio Sistema Neovate">
            <span className="inline-block w-8 h-8 rounded-md bg-brand-600 text-white grid place-items-center font-bold">N</span>
            <span className="hidden sm:inline">Sistema Neovate</span>
          </Link>

          <nav aria-label="Navegación principal" className="hidden md:flex items-center gap-1 ml-4">
            {items.map((it) => (
              <NavLink
                key={it.to}
                to={it.to}
                end={it.end}
                className={({ isActive }) =>
                  `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-brand-100 dark:bg-brand-800 text-brand-800 dark:text-brand-100"
                      : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                  }`
                }
              >
                {it.label}
              </NavLink>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            <button
              type="button"
              onClick={toggle}
              aria-label={theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
              aria-pressed={theme === "dark"}
              className="p-2 rounded-md text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              {theme === "dark" ? "☼" : "☾"}
            </button>

            {user && (
              <div className="hidden sm:flex items-center gap-2 text-sm">
                <span className="text-slate-600 dark:text-slate-400">{user.nombre}</span>
                <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200">
                  {user.rol}
                </span>
              </div>
            )}

            <button
              type="button"
              onClick={() => { logout(); navigate("/login"); }}
              className="px-3 py-2 rounded-md text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              Salir
            </button>

            <button
              type="button"
              className="md:hidden p-2 rounded-md text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
              onClick={() => setOpen((o) => !o)}
              aria-label="Menú"
              aria-expanded={open}
              aria-controls="mobile-menu"
            >
              ☰
            </button>
          </div>
        </div>

        {open && (
          <nav id="mobile-menu" aria-label="Navegación móvil" className="md:hidden border-t border-slate-200 dark:border-slate-700 px-4 py-2 space-y-1">
            {items.map((it) => (
              <NavLink
                key={it.to}
                to={it.to}
                end={it.end}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `block px-3 py-2 rounded-md text-sm font-medium ${
                    isActive
                      ? "bg-brand-100 dark:bg-brand-800 text-brand-800 dark:text-brand-100"
                      : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                  }`
                }
              >
                {it.label}
              </NavLink>
            ))}
          </nav>
        )}
      </header>

      <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 dark:border-slate-700 px-4 sm:px-6 py-4 text-xs text-slate-500 dark:text-slate-400 text-center">
        Sistema Neovate · Validación y Seguimiento de Pagos de Seguridad Social
      </footer>
    </div>
  );
}
