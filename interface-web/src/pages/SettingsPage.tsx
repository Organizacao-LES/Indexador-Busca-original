import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";

const SettingsPage = () => {
  return (
    <div className="max-w-2xl animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-6">Configurações</h1>

      <div className="space-y-6">
        <div className="glass-card p-5 space-y-4">
          <h3 className="font-semibold text-foreground">Geral</h3>
          <Separator />
          <div className="space-y-1.5">
            <Label>Nome da instância</Label>
            <Input defaultValue="IFESDOC - Campus Serra" />
          </div>
          <div className="space-y-1.5">
            <Label>URL base da API</Label>
            <Input defaultValue="https://api.ifesdoc.ifes.edu.br" />
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
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-foreground">OCR habilitado</p>
              <p className="text-xs text-muted-foreground">Reconhecimento óptico em documentos digitalizados</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="space-y-1.5">
            <Label>Tamanho máximo de arquivo (MB)</Label>
            <Input type="number" defaultValue="50" className="w-32" />
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
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-foreground">Relatório semanal</p>
              <p className="text-xs text-muted-foreground">Resumo de atividades enviado toda segunda-feira</p>
            </div>
            <Switch />
          </div>
        </div>

        <Button>Salvar Configurações</Button>
      </div>
    </div>
  );
};

export default SettingsPage;
