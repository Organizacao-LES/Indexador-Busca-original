import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

type RoleRouteProps = {
  allow: "admin";
};

export function RoleRoute({ allow }: RoleRouteProps) {
  const { isLoading, isAdmin } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted">
        <div className="glass-card px-6 py-4 text-sm text-muted-foreground">
          Carregando sessão...
        </div>
      </div>
    );
  }

  if (allow === "admin" && !isAdmin) {
    return <Navigate to="/busca" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
