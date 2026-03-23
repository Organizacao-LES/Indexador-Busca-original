import { useNavigate } from "react-router-dom";
import { Bell, Search, User } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { appEnv } from "@/lib/env";
import { useState } from "react";

export function AppHeader() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [quickSearch, setQuickSearch] = useState("");

  const handleQuickSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!quickSearch.trim()) {
      return;
    }

    navigate(`/resultados?q=${encodeURIComponent(quickSearch.trim())}`);
    setQuickSearch("");
  };

  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6 shrink-0">
      <form onSubmit={handleQuickSearch} className="flex items-center gap-4 flex-1 max-w-xl">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={quickSearch}
            onChange={(event) => setQuickSearch(event.target.value)}
            placeholder="Busca rápida..."
            className="pl-9 h-9 bg-muted border-0"
          />
        </div>
      </form>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4.5 w-4.5 text-muted-foreground" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
        </Button>

        <div className="flex items-center gap-3 ml-2 pl-4 border-l border-border">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium leading-none">{user?.name || appEnv.appName}</p>
            <p className="text-xs text-muted-foreground">{user?.email || "sem sessão"}</p>
          </div>
          <div className="h-9 w-9 rounded-full bg-primary flex items-center justify-center">
            <User className="h-4 w-4 text-primary-foreground" />
          </div>
        </div>
      </div>
    </header>
  );
}
