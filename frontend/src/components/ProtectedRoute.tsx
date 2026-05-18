import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export default function ProtectedRoute({ adminOnly = false }: { adminOnly?: boolean }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-full grid place-items-center p-8 text-slate-600 dark:text-slate-400" role="status" aria-live="polite">
        Cargando…
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  // Si tiene primer_login pendiente, lo forzamos a cambiar contraseña
  if (user.primer_login && location.pathname !== "/cambiar-password") {
    return <Navigate to="/cambiar-password" replace />;
  }

  if (adminOnly && user.rol !== "admin") {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-semibold">Acceso denegado</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">Necesitas rol admin para ver esta página.</p>
      </div>
    );
  }

  return <Outlet />;
}
