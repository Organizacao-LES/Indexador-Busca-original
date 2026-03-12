import { useState } from "react";
import { Upload, FileText, CheckCircle2, AlertCircle, X, Clock, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

const batchFiles = [
  { name: "relatorio_2025.pdf", size: "2.4 MB", status: "indexed" as const },
  { name: "edital_monitoria.pdf", size: "1.1 MB", status: "validated" as const },
  { name: "ata_reuniao.txt", size: "45 KB", status: "indexed" as const },
  { name: "planilha_notas.csv", size: "320 KB", status: "error" as const },
  { name: "portaria_032.pdf", size: "890 KB", status: "validated" as const },
];

const statusMap = {
  validated: { label: "Validado", variant: "secondary" as const, color: "text-info" },
  indexed: { label: "Indexado", variant: "default" as const, color: "text-success" },
  error: { label: "Falha", variant: "destructive" as const, color: "text-destructive" },
};

const ingestionHistory = [
  { date: "2025-08-12 14:32", file: "resolucao_45_2025.pdf", type: "Individual", result: "Sucesso", details: "Validado → Extraído → Indexado" },
  { date: "2025-08-12 14:30", file: "edital_monitoria.pdf", type: "Individual", result: "Sucesso", details: "Validado → Extraído → Indexado" },
  { date: "2025-08-11 16:42", file: "planilha_notas.csv", type: "Lote", result: "Falha", details: "Validação falhou: formato incompatível" },
  { date: "2025-08-11 16:40", file: "ata_reuniao.txt", type: "Lote", result: "Sucesso", details: "Validado → Extraído → Indexado" },
  { date: "2025-08-10 09:15", file: "portaria_032.pdf", type: "Individual", result: "Sucesso", details: "Validado → Extraído → Indexado" },
];

const IngestionPage = () => {
  const [dragOver, setDragOver] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [step, setStep] = useState<"idle" | "validating" | "validated" | "extracting" | "extracted" | "indexing" | "done">("idle");
  const { toast } = useToast();

  const handleValidate = () => {
    setStep("validating");
    setTimeout(() => {
      setStep("validated");
      toast({ title: "Documento validado", description: "Formato compatível, pronto para extração de texto (UC10)." });
    }, 1500);
  };

  const handleExtract = () => {
    setStep("extracting");
    setTimeout(() => {
      setStep("extracted");
      toast({ title: "Texto extraído", description: "Texto e metadados extraídos com sucesso (UC12)." });
    }, 1500);
  };

  const handleIndex = () => {
    setStep("indexing");
    setTimeout(() => {
      setStep("done");
      toast({ title: "Documento indexado", description: "Documento indexado e registrado no histórico (UC08)." });
    }, 2000);
  };

  const resetUpload = () => {
    setUploaded(false);
    setStep("idle");
  };

  const stepLabels = [
    { key: "upload", label: "Upload", done: uploaded },
    { key: "validate", label: "Validação", done: ["validated", "extracting", "extracted", "indexing", "done"].includes(step) },
    { key: "extract", label: "Extração", done: ["extracted", "indexing", "done"].includes(step) },
    { key: "index", label: "Indexação", done: step === "done" },
  ];

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-1">Ingestão de Documentos</h1>
      <p className="text-sm text-muted-foreground mb-6">Upload, validação, extração e indexação (UC08–UC14)</p>

      <Tabs defaultValue="individual">
        <TabsList>
          <TabsTrigger value="individual">Individual</TabsTrigger>
          <TabsTrigger value="batch">Em Lote</TabsTrigger>
          <TabsTrigger value="history">Histórico de Ingestão</TabsTrigger>
        </TabsList>

        <TabsContent value="individual" className="mt-4 space-y-4">
          {/* Pipeline steps */}
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 justify-between">
              {stepLabels.map((s, i) => (
                <div key={s.key} className="flex items-center gap-2 flex-1">
                  <div className={`flex items-center gap-2 text-sm font-medium ${s.done ? "text-success" : "text-muted-foreground"}`}>
                    <div className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold ${s.done ? "bg-success text-success-foreground" : "bg-muted text-muted-foreground"}`}>
                      {s.done ? "✓" : i + 1}
                    </div>
                    {s.label}
                  </div>
                  {i < stepLabels.length - 1 && (
                    <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Drop zone */}
          <div
            className={`border-2 border-dashed rounded-xl p-10 text-center transition-all duration-200 cursor-pointer ${
              dragOver ? "border-primary bg-accent" : uploaded ? "border-success bg-success/5" : "border-border hover:border-primary/50"
            }`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setDragOver(false); setUploaded(true); }}
            onClick={() => { if (!uploaded) setUploaded(true); }}
          >
            {uploaded ? (
              <div className="flex flex-col items-center gap-2">
                <CheckCircle2 className="h-10 w-10 text-success" />
                <p className="font-medium text-foreground">resolucao_45_2025.pdf</p>
                <p className="text-sm text-muted-foreground">2.4 MB · PDF</p>
                <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); resetUpload(); }}>
                  <X className="h-3 w-3 mr-1" /> Remover
                </Button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <Upload className="h-10 w-10 text-muted-foreground" />
                <p className="font-medium text-foreground">Arraste o arquivo aqui ou clique para selecionar</p>
                <p className="text-sm text-muted-foreground">Formatos aceitos: PDF, TXT, CSV (máx. 50MB)</p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label>Categoria</Label>
              <Select>
                <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="academico">Acadêmico</SelectItem>
                  <SelectItem value="administrativo">Administrativo</SelectItem>
                  <SelectItem value="pesquisa">Pesquisa</SelectItem>
                  <SelectItem value="extensao">Extensão</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Data do documento</Label>
              <Input type="date" />
            </div>
          </div>

          {/* Action buttons - sequential flow */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleValidate}
              disabled={!uploaded || step !== "idle"}
            >
              {step === "validating" ? "Validando..." : ["validated", "extracting", "extracted", "indexing", "done"].includes(step) ? "✓ Validado" : "1. Validar"}
            </Button>
            <Button
              variant="outline"
              onClick={handleExtract}
              disabled={step !== "validated"}
            >
              {step === "extracting" ? "Extraindo..." : ["extracted", "indexing", "done"].includes(step) ? "✓ Extraído" : "2. Extrair Texto"}
            </Button>
            <Button
              onClick={handleIndex}
              disabled={step !== "extracted"}
            >
              {step === "indexing" ? "Indexando..." : step === "done" ? "✓ Indexado" : "3. Indexar"}
            </Button>
          </div>

          {/* Status messages */}
          {step === "validated" && (
            <div className="glass-card p-4 flex items-center gap-3 border-l-4 border-l-success">
              <CheckCircle2 className="h-5 w-5 text-success shrink-0" />
              <div>
                <p className="text-sm font-medium text-foreground">Documento validado com sucesso (UC10)</p>
                <p className="text-xs text-muted-foreground">Formato compatível. Prossiga com a extração de texto.</p>
              </div>
            </div>
          )}
          {step === "extracted" && (
            <div className="glass-card p-4 flex items-center gap-3 border-l-4 border-l-info">
              <CheckCircle2 className="h-5 w-5 text-info shrink-0" />
              <div>
                <p className="text-sm font-medium text-foreground">Texto e metadados extraídos (UC12)</p>
                <p className="text-xs text-muted-foreground">2.340 tokens identificados. Pronto para indexação.</p>
              </div>
            </div>
          )}
          {step === "done" && (
            <div className="glass-card p-4 flex items-center gap-3 border-l-4 border-l-success">
              <CheckCircle2 className="h-5 w-5 text-success shrink-0" />
              <div>
                <p className="text-sm font-medium text-foreground">Ingestão concluída com sucesso</p>
                <p className="text-xs text-muted-foreground">Documento indexado e registrado no histórico de ingestão (UC14).</p>
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="batch" className="mt-4 space-y-4">
          <div
            className="border-2 border-dashed rounded-xl p-10 text-center border-border cursor-pointer hover:border-primary/50 transition-all duration-200"
          >
            <Upload className="h-10 w-10 text-muted-foreground mx-auto mb-2" />
            <p className="font-medium text-foreground">Arraste múltiplos arquivos ou clique para selecionar</p>
            <p className="text-sm text-muted-foreground">Formatos aceitos: PDF, TXT, CSV</p>
          </div>

          <div className="glass-card p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-foreground">Progresso geral (UC09)</span>
              <span className="text-sm text-muted-foreground">68%</span>
            </div>
            <Progress value={68} className="h-2" />
            <p className="text-xs text-muted-foreground mt-2">3 de 5 documentos processados. Falhas são registradas individualmente.</p>
          </div>

          <div className="glass-card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="text-left p-3 font-medium text-muted-foreground">Arquivo</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Tamanho</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-right p-3 font-medium text-muted-foreground">Ação</th>
                </tr>
              </thead>
              <tbody>
                {batchFiles.map((file, i) => (
                  <tr key={i} className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
                    <td className="p-3 flex items-center gap-2">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      {file.name}
                    </td>
                    <td className="p-3 text-muted-foreground">{file.size}</td>
                    <td className="p-3">
                      <Badge variant={statusMap[file.status].variant}>
                        {statusMap[file.status].label}
                      </Badge>
                    </td>
                    <td className="p-3 text-right">
                      {file.status === "error" && (
                        <Button variant="ghost" size="sm" className="text-destructive">
                          Reprocessar
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="history" className="mt-4 space-y-4">
          <div className="glass-card overflow-hidden">
            <div className="p-4 border-b border-border bg-muted/50">
              <h3 className="text-sm font-semibold text-foreground">Histórico de Ingestão (UC14)</h3>
              <p className="text-xs text-muted-foreground mt-1">Registro de todas as operações de ingestão para auditoria</p>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-3 font-medium text-muted-foreground">Data</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Arquivo</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Tipo</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Resultado</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Detalhes</th>
                </tr>
              </thead>
              <tbody>
                {ingestionHistory.map((item, i) => (
                  <tr key={i} className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
                    <td className="p-3 text-muted-foreground font-mono text-xs whitespace-nowrap">{item.date}</td>
                    <td className="p-3 text-foreground flex items-center gap-2">
                      <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                      {item.file}
                    </td>
                    <td className="p-3">
                      <Badge variant="secondary">{item.type}</Badge>
                    </td>
                    <td className="p-3">
                      <Badge variant={item.result === "Sucesso" ? "default" : "destructive"}
                        className={item.result === "Sucesso" ? "bg-success hover:bg-success/90" : ""}
                      >
                        {item.result}
                      </Badge>
                    </td>
                    <td className="p-3 text-muted-foreground text-xs">{item.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default IngestionPage;
