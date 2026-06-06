import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import CambiarPassword from "./pages/CambiarPassword";
import Dashboard from "./pages/Dashboard";
import Empresas from "./pages/Empresas";
import Historial from "./pages/Historial";
import Seguimiento from "./pages/Seguimiento";
import Usuarios from "./pages/Usuarios";
import SubirPlanilla from "./pages/SubirPlanilla";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/cambiar-password" element={<CambiarPassword />} />

        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="historial" element={<Historial />} />
          <Route path="seguimiento" element={<Seguimiento />} />

          {/* Empresas: visible para admin, analista y viewer — no para empresa */}
          <Route element={<ProtectedRoute allowedRoles={["admin", "analista", "viewer"]} />}>
            <Route path="empresas" element={<Empresas />} />
          </Route>

          {/* Subir planilla: admin, analista y empresa */}
          <Route element={<ProtectedRoute allowedRoles={["admin", "analista", "empresa"]} />}>
            <Route path="subir" element={<SubirPlanilla />} />
          </Route>

          {/* Usuarios: solo admin */}
          <Route element={<ProtectedRoute adminOnly />}>
            <Route path="usuarios" element={<Usuarios />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Route>
      </Route>
    </Routes>
  );
}
