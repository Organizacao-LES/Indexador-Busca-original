import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { PageError, PageLoader } from "@/components/PageState";
import { settingsService } from "@/lib/api/services";
import { useSettings } from "@/hooks/use-app-query";
import { useToast } from "@/hooks/use-toast";
import type { AppSettings } from "@/types/app";

const SettingsPage = () => {
  const { data, isLoading, isError, refetch } = useSettings();
  const { toast } = useToast();
  const [settings, setSettings] = useState<AppSettings | null>(null);

  useEffect(() => {
    if (data) {
      setSettings(data);
    }
  }, [data]);

  if (isError) {
    return <PageError title="Falha ao carregar configurações." onRetry={() => refetch()} />;
  }

  if (isLoading || !settings) {
    return <PageLoader label="Carregando configurações..." />;
  }

  const updateSetting = <K extends keyof AppSettings>(key: K, value: AppSettings[K]) => {
    setSettings((current) => current ? { ...current, [key]: value } : current);
  };

  const handleSave = async () => {
    await settingsService.update(settings);
    toast({
      title: "Configurações salvas",
      description: "Os parâmetros do frontend foram persistidos e podem ser conectados ao backend quando disponível.",
    });
  };

  return (
    <div className="max-w-2xl animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-6">Configurações</h1>

      <div className="space-y-6">
        <div className="glass-card p-5 space-y-4">
          <h3 className="font-semibold text-foreground">Geral</h3>
          <Separator />
          <div className="space-y-1.5">
            <Label>Nome da instância</Label>
            <Input value={settings.instanceName} onChange={(event) => updateSetting("instanceName", event.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>URL base da API</Label>
            <Input value={settings.apiBaseUrl} onChange={(event) => updateSetting("apiBaseUrl", event.target.value)} />
          </div>
        </div>

        <div className="glass-card p-5 space-y-4">
          <h3 className="font-semibold text-foreground">Indexação</h3>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-foreground">Indexação automática</p>
              <p className="text-xs text-muted-foreground">Indexar documentos automaticamente após upload</p>
            </div>
            <Switch checked={settings.autoIndexing} onCheckedChange={(value) => updateSetting("autoIndexing", value)} />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-foreground">OCR habilitado</p>
              <p className="text-xs text-muted-foreground">Reconhecimento óptico em documentos digitalizados</p>
            </div>
            <Switch checked={settings.ocrEnabled} onCheckedChange={(value) => updateSetting("ocrEnabled", value)} />
          </div>
          <div className="space-y-1.5">
            <Label>Tamanho máximo de arquivo (MB)</Label>
            <Input type="number" value={settings.maxFileSizeMb} onChange={(event) => updateSetting("maxFileSizeMb", Number(event.target.value))} className="w-32" />
          </div>
        </div>

        <div className="glass-card p-5 space-y-4">
          <h3 className="font-semibold text-foreground">Notificações</h3>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-foreground">Notificações por e-mail</p>
              <p className="text-xs text-muted-foreground">Receber alertas de erros de indexação</p>
            </div>
            <Switch checked={settings.emailNotifications} onCheckedChange={(value) => updateSetting("emailNotifications", value)} />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-foreground">Relatório semanal</p>
              <p className="text-xs text-muted-foreground">Resumo de atividades enviado toda segunda-feira</p>
            </div>
            <Switch checked={settings.weeklyReport} onCheckedChange={(value) => updateSetting("weeklyReport", value)} />
          </div>
        </div>

        <Button onClick={handleSave}>Salvar Configurações</Button>
      </div>
    </div>
  );
};

export default SettingsPage;
