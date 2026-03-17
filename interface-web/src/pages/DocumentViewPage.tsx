import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Download, Calendar, Tag, User, FileText, RefreshCw, Hash, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { documentService } from "@/lib/api/services";
import { PageError, PageLoader } from "@/components/PageState";
import { useDocument } from "@/hooks/use-app-query";

const DocumentViewPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { toast } = useToast();
  const [reindexing, setReindexing] = useState(false);
  const documentId = Number(id);
  const { data: document, isLoading, isError, refetch } = useDocument(documentId);

  const handleReindex = async () => {
    setReindexing(true);
    try {
      await documentService.reindex(documentId);
      toast({
        title: "Documento reindexado",
        description: "O documento foi reprocessado e o índice foi atualizado com sucesso (UC13).",
      });
    } finally {
      setReindexing(false);
    }
  };

  if (isLoading) {
    return <PageLoader label="Carregando documento..." />;
  }

  if (isError || !document) {
    return <PageError title="Falha ao carregar o documento." onRetry={() => refetch()} />;
  }

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
          Visualizador PDF embutido — {document.title}
        </div>

        <div className="p-6 border-b border-border">
          <h1 className="text-xl font-bold text-foreground mb-4">{document.title}</h1>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Tag className="h-3.5 w-3.5" />
              <Badge variant="secondary">{document.category}</Badge>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              {new Date(document.date).toLocaleDateString("pt-BR")}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <User className="h-3.5 w-3.5" />
              {document.author}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <FileText className="h-3.5 w-3.5" />
              {document.format} · {document.pages} páginas · {document.size}
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm mt-3">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Hash className="h-3.5 w-3.5" />
              Versão {document.version}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              Indexado em {document.indexedAt}
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="prose prose-sm max-w-none text-foreground whitespace-pre-line leading-relaxed">
            {document.content}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewPage;
