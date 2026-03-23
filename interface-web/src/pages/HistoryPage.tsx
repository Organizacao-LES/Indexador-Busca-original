import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { PageError, PageLoader } from "@/components/PageState";
import { useHistory } from "@/hooks/use-app-query";

const statusVariant: Record<string, "default" | "destructive" | "secondary"> = {
  success: "default",
  error: "destructive",
  info: "secondary",
  warning: "secondary",
};

const statusColors: Record<string, string> = {
  success: "bg-success hover:bg-success/90",
  warning: "bg-warning hover:bg-warning/90 text-warning-foreground",
};

const HistoryPage = () => {
  const { data, isLoading, isError, refetch } = useHistory();

  if (isLoading) {
    return <PageLoader label="Carregando histórico..." />;
  }

  if (isError || !data) {
    return <PageError title="Falha ao carregar histórico." onRetry={() => refetch()} />;
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Histórico</h1>
          <p className="text-sm text-muted-foreground mt-1">Registro de operações para auditoria (UC05, UC06, UC14, UC25)</p>
        </div>
        <Button variant="outline" className="gap-2">
          <Download className="h-4 w-4" />
          Exportar CSV
        </Button>
      </div>

      {/* Filters */}
      <div className="glass-card p-4 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="space-y-1.5">
            <Label className="text-xs">Período — De</Label>
            <Input type="date" className="text-xs" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Período — Até</Label>
            <Input type="date" className="text-xs" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Usuário</Label>
            <Select>
              <SelectTrigger><SelectValue placeholder="Todos" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="admin">admin@ifes.edu.br</SelectItem>
                <SelectItem value="joao">joao.oliveira@ifes.edu.br</SelectItem>
                <SelectItem value="maria">maria.santos@ifes.edu.br</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Tipo de Ação</Label>
            <Select>
              <SelectTrigger><SelectValue placeholder="Todas" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                <SelectItem value="busca">Busca</SelectItem>
                <SelectItem value="ingestao">Ingestão</SelectItem>
                <SelectItem value="indexacao">Indexação</SelectItem>
                <SelectItem value="falha">Falha de Indexação</SelectItem>
                <SelectItem value="reindexacao">Reindexação</SelectItem>
                <SelectItem value="usuario">Criação de Usuário</SelectItem>
                <SelectItem value="admin">Ação Administrativa</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="text-left p-3 font-medium text-muted-foreground">Data</th>
              <th className="text-left p-3 font-medium text-muted-foreground">Usuário</th>
              <th className="text-left p-3 font-medium text-muted-foreground">Tipo de Ação</th>
              <th className="text-left p-3 font-medium text-muted-foreground">Detalhes</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
                <td className="p-3 text-muted-foreground font-mono text-xs whitespace-nowrap">{row.date}</td>
                <td className="p-3 text-foreground">{row.user}</td>
                <td className="p-3">
                  <Badge
                    variant={statusVariant[row.status]}
                    className={statusColors[row.status] || ""}
                  >
                    {row.action}
                  </Badge>
                </td>
                <td className="p-3 text-muted-foreground">{row.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HistoryPage;
