import { useState } from "react";
import { Database, Clock, AlertTriangle, CheckCircle2, RefreshCw, TrendingUp } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

const logs = [
  { time: "14:32:01", message: "Iniciando indexação de 3 documentos...", type: "info" },
  { time: "14:32:03", message: "resolucao_45_2025.pdf — Extraindo texto (UC12)...", type: "info" },
  { time: "14:32:05", message: "resolucao_45_2025.pdf — Pré-processamento textual (UC15)...", type: "info" },
  { time: "14:32:08", message: "resolucao_45_2025.pdf — Tokenização concluída (2.340 tokens)", type: "success" },
  { time: "14:32:08", message: "resolucao_45_2025.pdf — Construção de índice invertido (UC16)", type: "success" },
  { time: "14:32:09", message: "edital_monitoria.pdf — Extraindo texto...", type: "info" },
  { time: "14:32:14", message: "edital_monitoria.pdf — Tokenização concluída (1.120 tokens)", type: "success" },
  { time: "14:32:14", message: "edital_monitoria.pdf — Índice atualizado incrementalmente (UC17)", type: "success" },
  { time: "14:32:15", message: "planilha_notas.csv — Formato incompatível com parser", type: "error" },
  { time: "14:32:15", message: "planilha_notas.csv — Documento registrado como inválido (UC11)", type: "error" },
  { time: "14:32:16", message: "Verificação de consistência documento-índice (UC18)...", type: "info" },
  { time: "14:32:17", message: "Indexação finalizada: 2 sucesso, 1 falha · Tempo total: 16s (UC19)", type: "info" },
];

const IndexStatusPage = () => {
  const { toast } = useToast();
  const [reindexing, setReindexing] = useState(false);

  const handleReindex = () => {
    setReindexing(true);
    setTimeout(() => {
      setReindexing(false);
      toast({ title: "Reindexação concluída", description: "Índice reconstruído com sucesso (UC13)." });
    }, 3000);
  };

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Status da Indexação</h1>
          <p className="text-sm text-muted-foreground mt-1">Processamento, índice e monitoramento (UC15–UC19)</p>
        </div>
        <Button onClick={handleReindex} disabled={reindexing} className="gap-2">
          <RefreshCw className={`h-4 w-4 ${reindexing ? "animate-spin" : ""}`} />
          {reindexing ? "Reindexando..." : "Reindexar Todos"}
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Database className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">1.247</p>
              <p className="text-xs text-muted-foreground">Documentos indexados</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-info/10 flex items-center justify-center">
              <Clock className="h-5 w-5 text-info" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">2.4s</p>
              <p className="text-xs text-muted-foreground">Tempo médio</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-success/10 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-success" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">96.2%</p>
              <p className="text-xs text-muted-foreground">Taxa de sucesso</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-destructive/10 flex items-center justify-center">
              <AlertTriangle className="h-5 w-5 text-destructive" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">3</p>
              <p className="text-xs text-muted-foreground">Erros detectados</p>
            </div>
          </div>
        </div>
      </div>

      {/* Current Progress */}
      <div className="glass-card p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-foreground">Indexação em andamento</h3>
          <Badge>Em processamento</Badge>
        </div>
        <Progress value={73} className="h-2.5 mb-2" />
        <p className="text-xs text-muted-foreground">73% concluído · Estimativa: 12 segundos restantes</p>
      </div>

      {/* Status summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass-card p-4 text-center">
          <p className="text-lg font-bold text-success">2</p>
          <p className="text-xs text-muted-foreground">Concluídos</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-lg font-bold text-info">0</p>
          <p className="text-xs text-muted-foreground">Em processamento</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-lg font-bold text-destructive">1</p>
          <p className="text-xs text-muted-foreground">Falhas</p>
        </div>
      </div>

      {/* Log */}
      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-border">
          <h3 className="text-sm font-semibold text-foreground">Log de Processamento em Tempo Real</h3>
        </div>
        <div className="divide-y divide-border max-h-96 overflow-y-auto">
          {logs.map((log, i) => (
            <div key={i} className="flex items-start gap-3 p-3 text-sm hover:bg-muted/30 transition-colors">
              <span className="text-xs text-muted-foreground font-mono whitespace-nowrap mt-0.5">{log.time}</span>
              {log.type === "success" && <CheckCircle2 className="h-4 w-4 text-success shrink-0 mt-0.5" />}
              {log.type === "error" && <AlertTriangle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />}
              {log.type === "info" && <Database className="h-4 w-4 text-info shrink-0 mt-0.5" />}
              <span className={log.type === "error" ? "text-destructive" : "text-foreground"}>{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default IndexStatusPage;
