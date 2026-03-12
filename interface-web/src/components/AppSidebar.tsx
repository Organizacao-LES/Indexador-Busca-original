import { NavLink, useLocation } from "react-router-dom";
import {
  Search,
  FileUp,
  Database,
  BarChart3,
  Clock,
  Users,
  Settings,
  LogOut,
  FileText,
} from "lucide-react";

const navItems = [
  { title: "Busca", path: "/busca", icon: Search },
  { title: "Ingestão", path: "/ingestao", icon: FileUp },
  { title: "Indexação", path: "/indexacao", icon: Database },
  { title: "Métricas", path: "/metricas", icon: BarChart3 },
  { title: "Histórico", path: "/historico", icon: Clock },
  { title: "Gestão de Usuários", path: "/usuarios", icon: Users },
  { title: "Configurações", path: "/configuracoes", icon: Settings },
];

export function AppSidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 min-h-screen bg-sidebar flex flex-col border-r border-sidebar-border shrink-0">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-sidebar-border">
        <FileText className="h-7 w-7 text-sidebar-primary mr-3" />
        <span className="text-xl font-bold text-sidebar-accent-foreground tracking-tight">
          IFESDOC
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`sidebar-link ${isActive ? "sidebar-link-active" : "sidebar-link-inactive"}`}
            >
              <item.icon className="h-4.5 w-4.5 shrink-0" />
              <span>{item.title}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="p-3 border-t border-sidebar-border">
        <NavLink
          to="/login"
          className="sidebar-link sidebar-link-inactive"
        >
          <LogOut className="h-4.5 w-4.5 shrink-0" />
          <span>Sair</span>
        </NavLink>
      </div>
    </aside>
  );
}
