import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
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
  const location = useLocation();
  const { data, isLoading, isError, refetch } = useSettings();
  const { toast } = useToast();
  const [settings, setSettings] = useState<AppSettings | null>(null);

  useEffect(() => {
    if (data) {
      setSettings(data);
    }
  }, [data]);

  useEffect(() => {
    if (!settings || !location.hash) {
      return;
    }

    const target = window.document.getElementById(location.hash.slice(1));
    target?.scrollIntoView({ behavior: "smooth", block: "center" });
    target?.classList.add("ring-2", "ring-primary", "ring-offset-2", "ring-offset-background");

    const timeout = window.setTimeout(() => {
      target?.classList.remove("ring-2", "ring-primary", "ring-offset-2", "ring-offset-background");
    }, 1800);

    return () => window.clearTimeout(timeout);
  }, [location.hash, settings]);

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
    try {
      await settingsService.update(settings);
      toast({
        title: "Configurações salvas",
        description: "Os parâmetros foram persistidos para esta instalação.",
      });
    } catch {
      toast({
        title: "Falha ao salvar configurações",
        description: "Não foi possível persistir os parâmetros informados.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="max-w-2xl animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-6">Configurações</h1>

      <div className="space-y-6">
        <div id="geral" className="glass-card p-5 space-y-4 scroll-mt-24 transition-shadow">
          <h3 className="font-semibold text-foreground">Geral</h3>
          <Separator />
          <div id="instanceName" className="space-y-1.5 rounded-lg p-2 scroll-mt-24 transition-shadow">
            <Label>Nome da instância</Label>
            <Input value={settings.instanceName} onChange={(event) => updateSetting("instanceName", event.target.value)} />
          </div>
          <div id="apiBaseUrl" className="space-y-1.5 rounded-lg p-2 scroll-mt-24 transition-shadow">
            <Label>URL base da API</Label>
            <Input value={settings.apiBaseUrl} onChange={(event) => updateSetting("apiBaseUrl", event.target.value)} />
          </div>
        </div>

        <div id="indexacao" className="glass-card p-5 space-y-4 scroll-mt-24 transition-shadow">
          <h3 className="font-semibold text-foreground">Indexação</h3>
          <Separator />
          <div id="autoIndexing" className="flex items-center justify-between rounded-lg p-2 scroll-mt-24 transition-shadow">
            <div>
              <p className="text-sm font-medium text-foreground">Indexação automática</p>
              <p className="text-xs text-muted-foreground">Indexar documentos automaticamente após upload</p>
            </div>
            <Switch checked={settings.autoIndexing} onCheckedChange={(value) => updateSetting("autoIndexing", value)} />
          </div>
          <div id="ocrEnabled" className="flex items-center justify-between rounded-lg p-2 scroll-mt-24 transition-shadow">
            <div>
              <p className="text-sm font-medium text-foreground">OCR habilitado</p>
              <p className="text-xs text-muted-foreground">Reconhecimento óptico em documentos digitalizados</p>
            </div>
            <Switch checked={settings.ocrEnabled} onCheckedChange={(value) => updateSetting("ocrEnabled", value)} />
          </div>
          <div id="maxFileSizeMb" className="space-y-1.5 rounded-lg p-2 scroll-mt-24 transition-shadow">
            <Label>Tamanho máximo de arquivo (MB)</Label>
            <Input type="number" value={settings.maxFileSizeMb} onChange={(event) => updateSetting("maxFileSizeMb", Number(event.target.value))} className="w-32" />
          </div>
        </div>

        <div id="notificacoes" className="glass-card p-5 space-y-4 scroll-mt-24 transition-shadow">
          <h3 className="font-semibold text-foreground">Notificações</h3>
          <Separator />
          <div id="emailNotifications" className="flex items-center justify-between rounded-lg p-2 scroll-mt-24 transition-shadow">
            <div>
              <p className="text-sm font-medium text-foreground">Notificações por e-mail</p>
              <p className="text-xs text-muted-foreground">Receber alertas de erros de indexação</p>
            </div>
            <Switch checked={settings.emailNotifications} onCheckedChange={(value) => updateSetting("emailNotifications", value)} />
          </div>
          <div id="weeklyReport" className="flex items-center justify-between rounded-lg p-2 scroll-mt-24 transition-shadow">
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
