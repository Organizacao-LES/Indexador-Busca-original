import { useState, type ElementType } from "react";
import { Edit, UserX, UserCheck, Plus, Shield, ShieldCheck } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { PageError, PageLoader } from "@/components/PageState";
import { useUsers } from "@/hooks/use-app-query";
import { userService } from "@/lib/api/services";
import type { UserRole, UserSummary } from "@/types/app";

const roleIcons: Record<UserRole, ElementType> = {
  Administrador: ShieldCheck,
  Usuário: Shield,
};

const UsersPage = () => {
  const { data, isLoading, isError, refetch } = useUsers();
  const [editingUser, setEditingUser] = useState<UserSummary | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: "",
    login: "",
    email: "",
    password: "",
    role: "Usuário" as UserRole,
  });
  const [editForm, setEditForm] = useState({
    name: "",
    login: "",
    email: "",
    role: "Usuário" as UserRole,
  });
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const reloadUsers = async () => {
    await queryClient.invalidateQueries({ queryKey: ["users"] });
    await refetch();
  };

  const createMutation = useMutation({
    mutationFn: userService.create,
    onSuccess: async () => {
      setCreateOpen(false);
      setCreateForm({ name: "", login: "", email: "", password: "", role: "Usuário" });
      await reloadUsers();
      toast({
        title: "Usuário cadastrado",
        description: "Novo usuário criado com sucesso. Ação registrada no histórico administrativo.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Falha ao cadastrar usuário",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: typeof editForm }) =>
      userService.update(id, payload),
    onSuccess: async () => {
      setEditOpen(false);
      setEditingUser(null);
      await reloadUsers();
      toast({
        title: "Usuário atualizado",
        description: "Perfil de acesso alterado com sucesso. Ação registrada no histórico.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Falha ao atualizar usuário",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, active }: { id: number; active: boolean }) =>
      userService.toggleActive(id, active),
    onSuccess: async (user) => {
      await reloadUsers();
      toast({
        title: user.active ? "Usuário ativado" : "Usuário inativado",
        description: `${user.name} foi ${user.active ? "ativado" : "inativado"} com sucesso. Ação registrada no histórico.`,
        variant: user.active ? "default" : "destructive",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Falha ao alterar status do usuário",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  if (isLoading) {
    return <PageLoader label="Carregando usuários..." />;
  }

  if (isError) {
    return <PageError title="Falha ao carregar usuários." onRetry={() => refetch()} />;
  }

  const effectiveUsers = data || [];

  const toggleActive = (id: number) => {
    const user = effectiveUsers.find((u) => u.id === id);
    if (!user) return;
    toggleActiveMutation.mutate({ id, active: !user.active });
  };

  const handleCreate = () => {
    createMutation.mutate(createForm);
  };

  const handleEdit = (user: UserSummary) => {
    setEditingUser(user);
    setEditForm({
      name: user.name,
      login: user.login,
      email: user.email,
      role: user.role,
    });
    setEditOpen(true);
  };

  const handleSaveEdit = () => {
    if (!editingUser) return;
    updateMutation.mutate({ id: editingUser.id, payload: editForm });
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
                <Input
                  placeholder="Nome completo do usuário"
                  value={createForm.name}
                  onChange={(event) => setCreateForm((current) => ({ ...current, name: event.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Login</Label>
                <Input
                  placeholder="Login de acesso"
                  value={createForm.login}
                  onChange={(event) => setCreateForm((current) => ({ ...current, login: event.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>E-mail institucional</Label>
                <Input
                  type="email"
                  placeholder="email@ifes.edu.br"
                  value={createForm.email}
                  onChange={(event) => setCreateForm((current) => ({ ...current, email: event.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Senha</Label>
                <Input
                  type="password"
                  placeholder="Senha de acesso"
                  value={createForm.password}
                  onChange={(event) => setCreateForm((current) => ({ ...current, password: event.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Perfil de Acesso</Label>
                <Select
                  value={createForm.role === "Administrador" ? "admin" : "usuario"}
                  onValueChange={(value) => setCreateForm((current) => ({
                    ...current,
                    role: value === "admin" ? "Administrador" : "Usuário",
                  }))}
                >
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
              <Button onClick={handleCreate} disabled={createMutation.isPending}>Cadastrar Usuário</Button>
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
                <Input
                  value={editForm.name}
                  onChange={(event) => setEditForm((current) => ({ ...current, name: event.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Login</Label>
                <Input
                  value={editForm.login}
                  onChange={(event) => setEditForm((current) => ({ ...current, login: event.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>E-mail</Label>
                <Input
                  value={editForm.email}
                  onChange={(event) => setEditForm((current) => ({ ...current, email: event.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Perfil de Acesso</Label>
                <Select
                  value={editForm.role === "Administrador" ? "admin" : "usuario"}
                  onValueChange={(value) => setEditForm((current) => ({
                    ...current,
                    role: value === "admin" ? "Administrador" : "Usuário",
                  }))}
                >
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
            <Button onClick={handleSaveEdit} disabled={updateMutation.isPending}>Salvar Alterações</Button>
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
            {effectiveUsers.map((user) => {
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
