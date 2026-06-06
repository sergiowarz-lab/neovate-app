import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import type { Rol } from "../types";

interface Props {
  adminOnly?: boolean;
  allowedRoles?: Rol[];
}

export default function ProtectedRoute({ adminOnly = false, allowedRoles }: Props) {
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

  if (user.primer_login && location.pathname !== "/cambiar-password") {
    return <Navigate to="/cambiar-password" replace />;
  }

  if (adminOnly && user.rol !== "admin") {
    return <Denied />;
  }

  if (allowedRoles && !allowedRoles.includes(user.rol)) {
    return <Denied />;
  }

  return <Outlet />;
}

function Denied() {
  return (
    <div className="p-8 text-center">
      <h1 className="text-2xl font-semibold">Acceso denegado</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-400">No tienes permiso para ver esta página.</p>
    </div>
  );
}
