import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ArrowLeft, FileText, Calendar, Tag, Eye, Download, SearchX, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

const mockResults = [
  { id: 1, title: "Resolução Normativa nº 45/2025 - Normas Acadêmicas", snippet: "Estabelece as normas para o funcionamento dos cursos de graduação, incluindo <mark>resolução</mark> sobre matrículas e avaliações...", category: "Acadêmico", type: "PDF", date: "2025-08-12", relevance: 95 },
  { id: 2, title: "Edital de Seleção 012/2025 - Programa de Monitoria", snippet: "O Instituto Federal do Espírito Santo torna público o <mark>edital</mark> para seleção de monitores para o semestre 2025/2...", category: "Acadêmico", type: "PDF", date: "2025-07-28", relevance: 88 },
  { id: 3, title: "Relatório de Gestão 2024 - Campus Serra", snippet: "Apresenta os resultados alcançados no exercício de 2024, contemplando indicadores de <mark>gestão</mark> acadêmica e administrativa...", category: "Administrativo", type: "PDF", date: "2025-03-15", relevance: 76 },
  { id: 4, title: "Plano de Desenvolvimento Institucional 2024-2028", snippet: "Define as diretrizes estratégicas e metas institucionais para o quinquênio, abordando <mark>plano</mark> de expansão e qualidade...", category: "Administrativo", type: "PDF", date: "2024-12-10", relevance: 72 },
  { id: 5, title: "Portaria nº 234/2025 - Comissão de Avaliação", snippet: "Designa os membros da comissão responsável pela avaliação institucional do período letivo 2025/1...", category: "Administrativo", type: "TXT", date: "2025-06-01", relevance: 64 },
];

const ResultsPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = 3;

  const hasResults = query.toLowerCase() !== "xyz123";

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate("/busca")}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-xl font-semibold text-foreground">Resultados da busca</h1>
            <p className="text-sm text-muted-foreground">
              {hasResults ? (
                <>{mockResults.length} documentos encontrados para "<span className="font-medium text-foreground">{query}</span>"</>
              ) : (
                <>Nenhum resultado para "<span className="font-medium text-foreground">{query}</span>"</>
              )}
            </p>
          </div>
        </div>
        {hasResults && (
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-1.5">
              <Download className="h-3.5 w-3.5" />
              CSV
            </Button>
            <Button variant="outline" size="sm" className="gap-1.5">
              <Download className="h-3.5 w-3.5" />
              PDF
            </Button>
          </div>
        )}
      </div>

      {!hasResults ? (
        <div className="glass-card p-12 text-center">
          <SearchX className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-foreground mb-2">Nenhuma correspondência encontrada</h2>
          <p className="text-sm text-muted-foreground max-w-md mx-auto mb-4">
            Sua consulta não retornou resultados. Tente refinar os termos de busca ou utilize filtros diferentes.
          </p>
          <Button variant="outline" onClick={() => navigate("/busca")}>
            Nova Busca
          </Button>
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {mockResults.map((doc) => (
              <div key={doc.id} className="glass-card p-5 hover:shadow-md transition-all duration-200">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <FileText className="h-4 w-4 text-primary shrink-0" />
                      <h3 className="font-semibold text-foreground truncate">{doc.title}</h3>
                    </div>
                    <p
                      className="text-sm text-muted-foreground line-clamp-2 mb-3 [&_mark]:highlight-term [&_mark]:bg-transparent"
                      dangerouslySetInnerHTML={{ __html: doc.snippet }}
                    />
                    <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
                      <span className="flex items-center gap-1">
                        <Tag className="h-3 w-3" />
                        <Badge variant="secondary" className="text-xs px-2 py-0">{doc.category}</Badge>
                      </span>
                      <Badge variant="outline" className="text-xs px-2 py-0">{doc.type}</Badge>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(doc.date).toLocaleDateString("pt-BR")}
                      </span>
                      <span className="flex items-center gap-1.5">
                        Relevância
                        <Progress value={doc.relevance} className="w-16 h-1.5" />
                        <span className="font-medium text-foreground">{doc.relevance}%</span>
                      </span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/documento/${doc.id}`)}
                    className="shrink-0 gap-1.5"
                  >
                    <Eye className="h-3.5 w-3.5" />
                    Visualizar
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center gap-2 mt-6">
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(currentPage - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            {[1, 2, 3].map((page) => (
              <Button
                key={page}
                variant={page === currentPage ? "default" : "outline"}
                size="sm"
                className="w-9"
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </Button>
            ))}
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(currentPage + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default ResultsPage;
