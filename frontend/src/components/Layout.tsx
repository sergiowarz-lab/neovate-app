import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { useTheme } from "../theme/useTheme";
import { useState } from "react";
import { usePushNotifications } from "../hooks/usePushNotifications";
import { AnimatePresence, motion } from "motion/react";

/* ── Sidebar icons (inline SVG) ────────────────────────── */
const IconDash = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" className="w-[18px] h-[18px]">
    <rect x="2" y="2" width="7" height="7" rx="1.5"/><rect x="11" y="2" width="7" height="7" rx="1.5"/>
    <rect x="2" y="11" width="7" height="7" rx="1.5"/><rect x="11" y="11" width="7" height="7" rx="1.5"/>
  </svg>
);
const IconBuilding = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" className="w-[18px] h-[18px]">
    <path d="M4 3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V3zm2 1v12h8V4H6zm1 2h2v2H7V6zm4 0h2v2h-2V6zm-4 4h2v2H7v-2zm4 0h2v2h-2v-2z"/>
  </svg>
);
const IconHistory = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" className="w-[18px] h-[18px]">
    <path fillRule="evenodd" d="M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm1-12a1 1 0 1 0-2 0v4a1 1 0 0 0 .293.707l2.828 2.829a1 1 0 1 0 1.415-1.415L11 9.586V6z" clipRule="evenodd"/>
  </svg>
);
const IconChart = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" className="w-[18px] h-[18px]">
    <path d="M2 11a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-5zm6-4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V7zm6-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-2a1 1 0 0 1-1-1V4z"/>
  </svg>
);
const IconUsers = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" className="w-[18px] h-[18px]">
    <path d="M9 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0zm8 0a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM6 12a6 6 0 0 0-5.916 5h11.832A6 6 0 0 0 6 12zm8 0a5.97 5.97 0 0 0-2.943.775A7.97 7.97 0 0 1 13.6 17H20a6 6 0 0 0-6-5z"/>
  </svg>
);
const IconUpload = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" className="w-[18px] h-[18px]">
    <path fillRule="evenodd" d="M3 17a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H4a1 1 0 0 1-1-1zM6.293 6.707a1 1 0 0 1 0-1.414l3-3a1 1 0 0 1 1.414 0l3 3a1 1 0 0 1-1.414 1.414L11 5.414V13a1 1 0 1 1-2 0V5.414L7.707 6.707a1 1 0 0 1-1.414 0z" clipRule="evenodd"/>
  </svg>
);
const IconSun  = () => <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4"><path fillRule="evenodd" d="M10 2a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0V3a1 1 0 0 1 1-1zm4.95 2.636a1 1 0 0 1 0 1.414l-.707.707a1 1 0 1 1-1.414-1.414l.707-.707a1 1 0 0 1 1.414 0zM17 10a1 1 0 0 1-1 1h-1a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1zm-2.636 4.95a1 1 0 0 1-1.414 0l-.707-.707a1 1 0 0 1 1.414-1.414l.707.707a1 1 0 0 1 0 1.414zM10 15a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0v-1a1 1 0 0 1 1-1zm-4.95-1.05a1 1 0 0 1 0-1.414l.707-.707a1 1 0 0 1 1.414 1.414l-.707.707a1 1 0 0 1-1.414 0zM5 10a1 1 0 0 1-1 1H3a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1zm-.636-4.95a1 1 0 0 1 1.414 0l.707.707A1 1 0 0 1 5.071 7.17l-.707-.707a1 1 0 0 1 0-1.414zM10 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6z" clipRule="evenodd"/></svg>;
const IconMoon = () => <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4"><path d="M17.293 13.293A8 8 0 0 1 6.707 2.707a8.001 8.001 0 1 0 10.586 10.586z"/></svg>;
const IconLogout = () => <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4"><path fillRule="evenodd" d="M3 3a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h7a1 1 0 1 1 0 2H3a3 3 0 0 1-3-3V4a3 3 0 0 1 3-3h7a1 1 0 1 1 0 2H3zm11.293 2.293a1 1 0 0 1 1.414 0l3 3a1 1 0 0 1 0 1.414l-3 3a1 1 0 0 1-1.414-1.414L16.586 10 14.293 7.707a1 1 0 0 1 0-1.414z" clipRule="evenodd"/></svg>;

type NavItem = { to: string; label: string; Icon: React.FC; end?: boolean };

const ROUTE_NAMES: Record<string, string> = {
  "/": "Dashboard", "/empresas": "Empresas", "/historial": "Historial",
  "/seguimiento": "Seguimiento", "/usuarios": "Usuarios",
  "/subir": "Subir Planilla", "/cambiar-password": "Cambiar Contraseña",
};

export default function Layout() {
  const { user, logout } = useAuth();
  const { theme, toggle } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { soportado, suscrito, suscribirse, desuscribirse, cargando } = usePushNotifications();

  const NAV: NavItem[] = [
    { to: "/",            label: "Dashboard",      Icon: IconDash,     end: true },
    { to: "/historial",   label: "Historial",      Icon: IconHistory  },
    { to: "/seguimiento", label: "Seguimiento",    Icon: IconChart    },
  ];

  const canUpload = user?.rol === "admin" || user?.rol === "analista" || user?.rol === "empresa";
  const canSeeEmpresas = user?.rol === "admin" || user?.rol === "analista" || user?.rol === "viewer";

  const extra: NavItem[] = [
    ...(canSeeEmpresas ? [{ to: "/empresas", label: "Empresas", Icon: IconBuilding }] : []),
    ...(canUpload      ? [{ to: "/subir",    label: "Subir Planilla", Icon: IconUpload }] : []),
    ...(user?.rol === "admin" ? [{ to: "/usuarios", label: "Usuarios", Icon: IconUsers }] : []),
  ];

  const items = [...NAV, ...extra];
  const pageName = ROUTE_NAMES[location.pathname] ?? "Página";

  const sidebarLink = ({ isActive }: { isActive: boolean }) =>
    `relative group flex flex-col items-center justify-center w-10 h-10 rounded-xl transition-all duration-200 ${
      isActive
        ? "bg-brand-500/15 text-brand-400 shadow-[inset_0_0_0_1px_rgba(201,168,76,0.3)]"
        : "text-slate-500 dark:text-slate-600 hover:bg-brand-500/8 hover:text-brand-400"
    }`;

  return (
    <div className="flex min-h-screen bg-[#f1f0f7] dark:bg-[#0f0e17] text-slate-900 dark:text-[#e8e6f0]">

      {/* ── Fixed background orbs ─────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0" aria-hidden="true">
        <div className="orb-a absolute top-[-20%] left-[-10%] w-[700px] h-[700px] rounded-full bg-brand-400/5 dark:bg-brand-500/8 blur-[150px]" />
        <div className="orb-b absolute bottom-[-15%] right-[-10%] w-[600px] h-[600px] rounded-full bg-brand-600/4 dark:bg-brand-600/6 blur-[120px]" />
        <div className="orb-c absolute top-[45%] right-[35%] w-[350px] h-[350px] rounded-full bg-brand-400/3 dark:bg-brand-400/5 blur-[90px]" />
      </div>

      {/* ── Left sidebar (desktop) ────────────────────────── */}
      <aside className="hidden md:flex relative z-30 flex-col w-14 sticky top-0 h-screen shrink-0
                        bg-white/80 dark:bg-[#1a1825]/90 backdrop-blur-xl
                        border-r border-slate-200/60 dark:border-white/[0.06]">
        {/* Logo */}
        <div className="flex items-center justify-center h-14 border-b border-slate-200/60 dark:border-white/[0.06] shrink-0">
          <Link
            to="/"
            aria-label="Inicio"
            className="flex items-center justify-center w-9 h-9 rounded-xl
                       bg-brand-500 text-black dark:bg-black dark:text-brand-400
                       dark:border dark:border-brand-500/50
                       font-bold text-sm
                       hover:shadow-[0_0_18px_rgba(201,168,76,0.5)] transition-all duration-300"
          >
            N
          </Link>
        </div>

        {/* Nav items */}
        <nav aria-label="Navegación principal" className="flex-1 flex flex-col items-center gap-1 py-3 overflow-y-auto">
          {items.map((it) => (
            <NavLink key={it.to} to={it.to} end={it.end} className={sidebarLink} title={it.label}>
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-brand-400 rounded-r-full" />
                  )}
                  <it.Icon />
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Bottom actions */}
        <div className="flex flex-col items-center gap-1 py-3 border-t border-slate-200/60 dark:border-white/[0.06] shrink-0">
          <button
            onClick={toggle}
            aria-label="Cambiar tema"
            className="w-10 h-10 flex items-center justify-center rounded-xl text-slate-400 dark:text-slate-600 hover:bg-brand-500/8 hover:text-brand-400 transition-all"
          >
            {theme === "dark" ? <IconSun /> : <IconMoon />}
          </button>
          <button
            onClick={() => { logout(); navigate("/login"); }}
            aria-label="Salir"
            className="w-10 h-10 flex items-center justify-center rounded-xl text-slate-400 dark:text-slate-600 hover:bg-rose-500/8 hover:text-rose-400 transition-all"
          >
            <IconLogout />
          </button>
        </div>
      </aside>

      {/* ── Main area ─────────────────────────────────────── */}
      <div className="relative z-10 flex flex-col flex-1 min-w-0">

        {/* Top header */}
        <header className="relative header-gold-bar sticky top-0 z-20 flex items-center h-14 px-4 sm:px-5 gap-3
                           bg-white/80 dark:bg-[#1a1825]/80 backdrop-blur-xl
                           border-b border-slate-200/60 dark:border-white/[0.06] shrink-0">

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 transition-all"
            onClick={() => setMobileOpen((o) => !o)}
            aria-label="Menú"
          >
            {mobileOpen ? "✕" : "☰"}
          </button>

          {/* Breadcrumb */}
          <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-slate-500">
            <Link to="/" className="hover:text-brand-500 transition-colors">Inicio</Link>
            <span>/</span>
            <span className="text-slate-700 dark:text-[#e8e6f0]">{pageName}</span>
          </div>

          <div className="ml-auto flex items-center gap-3">
            {/* Botón notificaciones push */}
            {soportado && (
              <button
                onClick={suscrito ? desuscribirse : suscribirse}
                disabled={cargando}
                title={suscrito ? "Desactivar notificaciones" : "Activar notificaciones"}
                className={`w-8 h-8 flex items-center justify-center rounded-xl transition-all text-sm
                  ${suscrito
                    ? "bg-brand-500/20 text-brand-600 dark:text-brand-400 hover:bg-rose-500/10 hover:text-rose-400"
                    : "text-slate-400 dark:text-slate-600 hover:bg-brand-500/8 hover:text-brand-400"
                  } disabled:opacity-50`}
              >
                {suscrito ? "🔔" : "🔕"}
              </button>
            )}

            {/* Date indicator */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs
                            bg-slate-100/80 dark:bg-white/[0.04] border border-slate-200/60 dark:border-white/[0.07]
                            text-slate-500 dark:text-slate-500">
              <span>📅</span>
              <span>{new Date().toLocaleDateString("es-CO", { year:"numeric", month:"short", day:"2-digit" })}</span>
            </div>

            {/* User info */}
            {user && (
              <div className="flex items-center gap-2">
                <div className="hidden sm:block text-right">
                  <p className="text-xs font-medium text-slate-700 dark:text-[#e8e6f0] leading-none">{user.nombre}</p>
                  <p className="text-[10px] text-brand-600 dark:text-brand-500 uppercase tracking-wider leading-none mt-0.5">{user.rol}</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-brand-500/20 dark:bg-brand-500/15 border border-brand-400/30
                                flex items-center justify-center text-brand-700 dark:text-brand-400 font-bold text-xs">
                  {user.nombre?.charAt(0).toUpperCase() ?? "U"}
                </div>
              </div>
            )}
          </div>
        </header>

        {/* Mobile menu */}
        <AnimatePresence>
          {mobileOpen && (
            <motion.nav
              className="md:hidden relative z-20 border-b border-slate-200/60 dark:border-white/[0.06] px-4 py-2 space-y-1
                         bg-white/95 dark:bg-[#1a1825]/95 backdrop-blur-xl"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              {items.map((it) => (
                <NavLink
                  key={it.to}
                  to={it.to}
                  end={it.end}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? "bg-brand-500/10 text-brand-600 dark:text-brand-400"
                        : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5"
                    }`
                  }
                >
                  <it.Icon />
                  {it.label}
                </NavLink>
              ))}
            </motion.nav>
          )}
        </AnimatePresence>

        {/* Page content */}
        <main id="main-content" className="flex-1 p-4 sm:p-5 lg:p-6">
          <Outlet />
        </main>

        <footer className="px-5 py-3 text-[10px] text-slate-400 dark:text-slate-700 border-t border-slate-200/60 dark:border-white/[0.05]">
          Sistema Neovate · Validación y Seguimiento de Pagos SS
        </footer>
      </div>
    </div>
  );
}
