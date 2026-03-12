import { BarChart3, Clock, FileText, Search, TrendingUp, Hash } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const queryData = [
  { day: "Seg", consultas: 42 },
  { day: "Ter", consultas: 58 },
  { day: "Qua", consultas: 35 },
  { day: "Qui", consultas: 71 },
  { day: "Sex", consultas: 63 },
  { day: "Sáb", consultas: 12 },
  { day: "Dom", consultas: 8 },
];

const termsData = [
  { name: "resolução", value: 124 },
  { name: "edital", value: 98 },
  { name: "relatório", value: 76 },
  { name: "plano pedagógico", value: 54 },
  { name: "portaria", value: 41 },
];

const categoryData = [
  { name: "Acadêmico", value: 520 },
  { name: "Administrativo", value: 380 },
  { name: "Pesquisa", value: 210 },
  { name: "Extensão", value: 137 },
];

const COLORS = [
  "hsl(152, 45%, 32%)",
  "hsl(152, 35%, 45%)",
  "hsl(152, 25%, 55%)",
  "hsl(150, 20%, 65%)",
  "hsl(150, 15%, 75%)",
];

const CATEGORY_COLORS = [
  "hsl(152, 45%, 32%)",
  "hsl(210, 70%, 50%)",
  "hsl(38, 92%, 50%)",
  "hsl(0, 65%, 48%)",
];

const MetricsPage = () => {
  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Métricas e Relatórios</h1>
          <p className="text-sm text-muted-foreground mt-1">Monitoramento de desempenho do sistema (UC38–UC41)</p>
        </div>
        <Select defaultValue="7d">
          <SelectTrigger className="w-44">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">Últimos 7 dias</SelectItem>
            <SelectItem value="30d">Últimos 30 dias</SelectItem>
            <SelectItem value="90d">Últimos 90 dias</SelectItem>
            <SelectItem value="365d">Último ano</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Search className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">1.893</p>
              <p className="text-xs text-muted-foreground">Total de consultas</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-info/10 flex items-center justify-center">
              <Clock className="h-5 w-5 text-info" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">0.34s</p>
              <p className="text-xs text-muted-foreground">Tempo médio (UC39)</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-success/10 flex items-center justify-center">
              <FileText className="h-5 w-5 text-success" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">1.247</p>
              <p className="text-xs text-muted-foreground">Docs indexados</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">96.2%</p>
              <p className="text-xs text-muted-foreground">Taxa de sucesso</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-warning/10 flex items-center justify-center">
              <Hash className="h-5 w-5 text-warning" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">8.3</p>
              <p className="text-xs text-muted-foreground">Média resultados (UC40)</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-warning/10 flex items-center justify-center">
              <BarChart3 className="h-5 w-5 text-warning" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">289</p>
              <p className="text-xs text-muted-foreground">Consultas hoje</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-foreground mb-4">Consultas por dia</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={queryData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(200, 15%, 90%)" />
              <XAxis dataKey="day" tick={{ fontSize: 12 }} stroke="hsl(200, 10%, 45%)" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(200, 10%, 45%)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(0, 0%, 100%)",
                  border: "1px solid hsl(200, 15%, 90%)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="consultas" fill="hsl(152, 45%, 32%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-foreground mb-4">Documentos por categoria</h3>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width="50%" height={260}>
              <PieChart>
                <Pie data={categoryData} cx="50%" cy="50%" innerRadius={50} outerRadius={90} dataKey="value" paddingAngle={3}>
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(0, 0%, 100%)",
                    border: "1px solid hsl(200, 15%, 90%)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-2">
              {categoryData.map((cat, i) => (
                <div key={cat.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: CATEGORY_COLORS[i] }} />
                    <span className="text-foreground">{cat.name}</span>
                  </div>
                  <span className="text-muted-foreground font-mono">{cat.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-foreground mb-4">Termos mais buscados</h3>
        <div className="flex items-center gap-6">
          <ResponsiveContainer width="40%" height={220}>
            <PieChart>
              <Pie data={termsData} cx="50%" cy="50%" innerRadius={40} outerRadius={80} dataKey="value" paddingAngle={3}>
                {termsData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(0, 0%, 100%)",
                  border: "1px solid hsl(200, 15%, 90%)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex-1 space-y-2">
            {termsData.map((term, i) => (
              <div key={term.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: COLORS[i] }} />
                  <span className="text-foreground">{term.name}</span>
                </div>
                <span className="text-muted-foreground font-mono">{term.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsPage;
