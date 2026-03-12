import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

const historyData = [
  { date: "2025-08-12 14:32", user: "admin@ifes.edu.br", action: "Indexação", details: "resolucao_45_2025.pdf indexado com sucesso", status: "success" },
  { date: "2025-08-12 14:30", user: "joao.oliveira@ifes.edu.br", action: "Busca", details: 'Consulta: "resolução normativa" — 5 resultados', status: "info" },
  { date: "2025-08-12 13:15", user: "admin@ifes.edu.br", action: "Ingestão", details: "Upload de edital_monitoria.pdf (1.1 MB)", status: "success" },
  { date: "2025-08-11 16:42", user: "admin@ifes.edu.br", action: "Falha de Indexação", details: "planilha_notas.csv — falha na indexação (UC11)", status: "error" },
  { date: "2025-08-11 10:20", user: "maria.santos@ifes.edu.br", action: "Busca", details: 'Consulta: "edital 2025" — 3 resultados', status: "info" },
  { date: "2025-08-10 09:05", user: "admin@ifes.edu.br", action: "Criação de Usuário", details: "Novo usuário maria.santos@ifes.edu.br criado (UC01)", status: "success" },
  { date: "2025-08-10 09:04", user: "admin@ifes.edu.br", action: "Ação Administrativa", details: "Perfil de pedro.lima alterado para Administrador (UC03)", status: "success" },
  { date: "2025-08-09 17:30", user: "admin@ifes.edu.br", action: "Ingestão", details: "Upload em lote: 5 arquivos processados (UC09)", status: "success" },
  { date: "2025-08-09 11:00", user: "admin@ifes.edu.br", action: "Ação Administrativa", details: "Usuário ana.costa inativado (UC05)", status: "warning" },
  { date: "2025-08-08 15:20", user: "admin@ifes.edu.br", action: "Reindexação", details: "Documento portaria_032.pdf reindexado (UC13)", status: "success" },
];

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
            {historyData.map((row, i) => (
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
