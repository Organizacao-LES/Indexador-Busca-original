import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, SlidersHorizontal } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";

const SearchPage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/resultados?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <div className="max-w-3xl mx-auto pt-16 animate-fade-in">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-foreground mb-2">Buscar Documentos</h1>
        <p className="text-muted-foreground">
          Pesquise na base de documentos indexados do IFESDOC
        </p>
      </div>

      <form onSubmit={handleSearch}>
        <div className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Digite sua consulta (palavra-chave ou termos compostos)..."
              className="pl-12 h-12 text-base"
            />
          </div>
          <Button type="submit" className="h-12 px-8">
            Buscar
          </Button>
          <Button
            type="button"
            variant="outline"
            className="h-12"
            onClick={() => setShowFilters(!showFilters)}
          >
            <SlidersHorizontal className="h-4 w-4" />
          </Button>
        </div>

        {showFilters && (
          <div className="glass-card p-5 space-y-4 animate-fade-in">
            <h3 className="text-sm font-semibold text-foreground">Filtros Avançados (UC23)</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-1.5">
                <Label className="text-xs">Categoria</Label>
                <Select>
                  <SelectTrigger><SelectValue placeholder="Todas" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas</SelectItem>
                    <SelectItem value="academico">Acadêmico</SelectItem>
                    <SelectItem value="administrativo">Administrativo</SelectItem>
                    <SelectItem value="pesquisa">Pesquisa</SelectItem>
                    <SelectItem value="extensao">Extensão</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Tipo de Documento</Label>
                <Select>
                  <SelectTrigger><SelectValue placeholder="Todos" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    <SelectItem value="pdf">PDF</SelectItem>
                    <SelectItem value="txt">TXT</SelectItem>
                    <SelectItem value="csv">CSV</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Período — De</Label>
                <Input type="date" className="text-xs" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Período — Até</Label>
                <Input type="date" className="text-xs" />
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="space-y-1.5">
                <Label className="text-xs">Ordenar por</Label>
                <Select>
                  <SelectTrigger className="w-40"><SelectValue placeholder="Relevância" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="relevancia">Relevância</SelectItem>
                    <SelectItem value="data-desc">Data (Recente)</SelectItem>
                    <SelectItem value="data-asc">Data (Antiga)</SelectItem>
                    <SelectItem value="titulo">Título (A-Z)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Máx. resultados (UC22)</Label>
                <Select defaultValue="20">
                  <SelectTrigger className="w-24"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="10">10</SelectItem>
                    <SelectItem value="20">20</SelectItem>
                    <SelectItem value="50">50</SelectItem>
                    <SelectItem value="100">100</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        )}
      </form>

      {/* Recent searches */}
      <div className="mt-10">
        <h3 className="text-sm font-medium text-muted-foreground mb-3">Buscas recentes</h3>
        <div className="flex flex-wrap gap-2">
          {["resolução normativa", "edital 2025", "relatório gestão", "plano pedagógico"].map((term) => (
            <button
              key={term}
              onClick={() => { setQuery(term); navigate(`/resultados?q=${encodeURIComponent(term)}`); }}
              className="px-3 py-1.5 rounded-full text-sm bg-secondary text-secondary-foreground hover:bg-accent transition-colors"
            >
              {term}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
