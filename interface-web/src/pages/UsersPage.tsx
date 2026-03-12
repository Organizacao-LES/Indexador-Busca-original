import { useState } from "react";
import { Edit, UserX, UserCheck, Plus, Shield, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

const initialUsers = [
  { id: 1, name: "Carlos Silva", login: "admin", email: "admin@ifes.edu.br", role: "Administrador" as const, active: true },
  { id: 2, name: "João Oliveira", login: "joao.oliveira", email: "joao.oliveira@ifes.edu.br", role: "Usuário" as const, active: true },
  { id: 3, name: "Ana Costa", login: "ana.costa", email: "ana.costa@ifes.edu.br", role: "Usuário" as const, active: false },
  { id: 4, name: "Pedro Lima", login: "pedro.lima", email: "pedro.lima@ifes.edu.br", role: "Administrador" as const, active: true },
  { id: 5, name: "Maria Santos", login: "maria.santos", email: "maria.santos@ifes.edu.br", role: "Usuário" as const, active: true },
];

type Role = "Administrador" | "Usuário";

const roleIcons: Record<Role, React.ElementType> = {
  Administrador: ShieldCheck,
  Usuário: Shield,
};

const UsersPage = () => {
  const [users, setUsers] = useState(initialUsers);
  const [editingUser, setEditingUser] = useState<typeof initialUsers[0] | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const { toast } = useToast();

  const toggleActive = (id: number) => {
    const user = users.find((u) => u.id === id);
    if (!user) return;
    const newStatus = !user.active;
    setUsers(users.map((u) => (u.id === id ? { ...u, active: newStatus } : u)));
    toast({
      title: newStatus ? "Usuário ativado" : "Usuário inativado",
      description: `${user.name} foi ${newStatus ? "ativado" : "inativado"} com sucesso. Ação registrada no histórico.`,
      variant: newStatus ? "default" : "destructive",
    });
  };

  const handleCreate = () => {
    setCreateOpen(false);
    toast({
      title: "Usuário cadastrado",
      description: "Novo usuário criado com sucesso. Ação registrada no histórico administrativo.",
    });
  };

  const handleEdit = (user: typeof initialUsers[0]) => {
    setEditingUser(user);
    setEditOpen(true);
  };

  const handleSaveEdit = () => {
    setEditOpen(false);
    setEditingUser(null);
    toast({
      title: "Usuário atualizado",
      description: "Perfil de acesso alterado com sucesso. Ação registrada no histórico.",
    });
  };

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Gestão de Usuários</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Cadastro, edição e controle de perfis de acesso (UC01–UC06)
          </p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Cadastrar Usuário
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Cadastrar Novo Usuário</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <div className="space-y-1.5">
                <Label>Nome completo</Label>
                <Input placeholder="Nome completo do usuário" />
              </div>
              <div className="space-y-1.5">
                <Label>Login</Label>
                <Input placeholder="Login de acesso" />
              </div>
              <div className="space-y-1.5">
                <Label>E-mail institucional</Label>
                <Input type="email" placeholder="email@ifes.edu.br" />
              </div>
              <div className="space-y-1.5">
                <Label>Senha</Label>
                <Input type="password" placeholder="Senha de acesso" />
              </div>
              <div className="space-y-1.5">
                <Label>Perfil de Acesso</Label>
                <Select>
                  <SelectTrigger><SelectValue placeholder="Selecione o perfil" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Administrador</SelectItem>
                    <SelectItem value="usuario">Usuário</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <p className="text-xs text-muted-foreground">
                Apenas administradores autenticados podem cadastrar usuários. A ação será registrada no log administrativo.
              </p>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancelar</Button>
              <Button onClick={handleCreate}>Cadastrar Usuário</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Usuário</DialogTitle>
          </DialogHeader>
          {editingUser && (
            <div className="space-y-4 pt-2">
              <div className="space-y-1.5">
                <Label>Nome completo</Label>
                <Input defaultValue={editingUser.name} />
              </div>
              <div className="space-y-1.5">
                <Label>Login</Label>
                <Input defaultValue={editingUser.login} />
              </div>
              <div className="space-y-1.5">
                <Label>E-mail</Label>
                <Input defaultValue={editingUser.email} />
              </div>
              <div className="space-y-1.5">
                <Label>Perfil de Acesso</Label>
                <Select defaultValue={editingUser.role === "Administrador" ? "admin" : "usuario"}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Administrador</SelectItem>
                    <SelectItem value="usuario">Usuário</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <p className="text-xs text-muted-foreground">
                Alterações de perfil serão refletidas no próximo login do usuário.
              </p>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>Cancelar</Button>
            <Button onClick={handleSaveEdit}>Salvar Alterações</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="glass-card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="text-left p-3 font-medium text-muted-foreground">Nome</th>
              <th className="text-left p-3 font-medium text-muted-foreground">Login</th>
              <th className="text-left p-3 font-medium text-muted-foreground">E-mail</th>
              <th className="text-left p-3 font-medium text-muted-foreground">Perfil</th>
              <th className="text-left p-3 font-medium text-muted-foreground">Status</th>
              <th className="text-right p-3 font-medium text-muted-foreground">Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => {
              const RoleIcon = roleIcons[user.role];
              return (
                <tr key={user.id} className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
                  <td className="p-3 font-medium text-foreground">{user.name}</td>
                  <td className="p-3 text-muted-foreground font-mono text-xs">{user.login}</td>
                  <td className="p-3 text-muted-foreground">{user.email}</td>
                  <td className="p-3">
                    <Badge variant={user.role === "Administrador" ? "default" : "secondary"} className="gap-1">
                      <RoleIcon className="h-3 w-3" />
                      {user.role}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge
                      variant={user.active ? "default" : "destructive"}
                      className={user.active ? "bg-success hover:bg-success/90" : ""}
                    >
                      {user.active ? "Ativo" : "Inativo"}
                    </Badge>
                  </td>
                  <td className="p-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        title="Editar usuário"
                        onClick={() => handleEdit(user)}
                      >
                        <Edit className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        title={user.active ? "Inativar usuário" : "Ativar usuário"}
                        onClick={() => toggleActive(user.id)}
                      >
                        {user.active ? (
                          <UserX className="h-3.5 w-3.5 text-destructive" />
                        ) : (
                          <UserCheck className="h-3.5 w-3.5 text-success" />
                        )}
                      </Button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UsersPage;
