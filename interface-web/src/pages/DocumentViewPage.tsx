import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Download, Calendar, Tag, User, FileText, RefreshCw, Hash, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

const mockDoc = {
  id: 1,
  title: "Resolução Normativa nº 45/2025 - Normas Acadêmicas",
  category: "Acadêmico",
  type: "PDF",
  date: "2025-08-12",
  author: "Conselho Superior",
  format: "PDF",
  pages: 12,
  version: 2,
  indexedAt: "2025-08-12 14:32",
  size: "2.4 MB",
  content: `Art. 1º Esta Resolução estabelece as normas gerais para o funcionamento dos cursos de graduação do Instituto Federal do Espírito Santo - IFES.

Art. 2º A organização didático-pedagógica dos cursos de graduação observará os seguintes princípios:
I - flexibilidade curricular e interdisciplinaridade;
II - articulação entre ensino, pesquisa e extensão;
III - incentivo à inovação e ao empreendedorismo;
IV - valorização da diversidade e da inclusão social.

Art. 3º O ingresso nos cursos de graduação dar-se-á por meio de processo seletivo, conforme edital específico publicado pela instituição.

Parágrafo único. Poderão ser utilizados como forma de ingresso:
a) Sistema de Seleção Unificada (SiSU);
b) Vestibular próprio;
c) Transferência externa;
d) Portador de diploma de graduação.

Art. 4º A matrícula será realizada semestralmente, conforme calendário acadêmico aprovado pelo Conselho de Ensino.

§1º O discente que não efetuar a matrícula no prazo estabelecido terá seu vínculo com a instituição cancelado.

§2º É assegurado ao discente o direito de trancamento de matrícula por até 2 (dois) semestres consecutivos ou 4 (quatro) alternados.

Art. 5º A avaliação da aprendizagem será processual, contínua e cumulativa, prevalecendo os aspectos qualitativos sobre os quantitativos.`,
};

const DocumentViewPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { toast } = useToast();
  const [reindexing, setReindexing] = useState(false);

  const handleReindex = () => {
    setReindexing(true);
    setTimeout(() => {
      setReindexing(false);
      toast({
        title: "Documento reindexado",
        description: "O documento foi reprocessado e o índice foi atualizado com sucesso (UC13).",
      });
    }, 2000);
  };

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Voltar
        </Button>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="gap-2"
            onClick={handleReindex}
            disabled={reindexing}
          >
            <RefreshCw className={`h-4 w-4 ${reindexing ? "animate-spin" : ""}`} />
            {reindexing ? "Reindexando..." : "Reindexar (Admin)"}
          </Button>
          <Button className="gap-2">
            <Download className="h-4 w-4" />
            Download
          </Button>
        </div>
      </div>

      <div className="glass-card">
        {/* PDF Viewer Placeholder */}
        <div className="bg-muted/50 border-b border-border p-4 flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <FileText className="h-5 w-5" />
          Visualizador PDF embutido — {mockDoc.title}
        </div>

        <div className="p-6 border-b border-border">
          <h1 className="text-xl font-bold text-foreground mb-4">{mockDoc.title}</h1>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Tag className="h-3.5 w-3.5" />
              <Badge variant="secondary">{mockDoc.category}</Badge>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              {new Date(mockDoc.date).toLocaleDateString("pt-BR")}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <User className="h-3.5 w-3.5" />
              {mockDoc.author}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <FileText className="h-3.5 w-3.5" />
              {mockDoc.format} · {mockDoc.pages} páginas · {mockDoc.size}
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm mt-3">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Hash className="h-3.5 w-3.5" />
              Versão {mockDoc.version}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              Indexado em {mockDoc.indexedAt}
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="prose prose-sm max-w-none text-foreground whitespace-pre-line leading-relaxed">
            {mockDoc.content}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewPage;
