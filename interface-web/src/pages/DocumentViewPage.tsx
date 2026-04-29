import { useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Download,
  Calendar,
  Tag,
  User,
  FileText,
  RefreshCw,
  Hash,
  Clock,
  ChevronLeft,
  ChevronRight,
  FileJson,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { documentService } from "@/lib/api/services";
import { PageError, PageLoader } from "@/components/PageState";
import { useDocument } from "@/hooks/use-app-query";

type DocumentNavigationState = {
  resultIds?: number[];
  query?: string;
  from?: string;
};

const saveBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob);
  const anchor = window.document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  window.document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
};

const DocumentViewPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();
  const { toast } = useToast();
  const { isAdmin } = useAuth();
  const [reindexing, setReindexing] = useState(false);
  const [exporting, setExporting] = useState<string | null>(null);
  const documentId = Number(id);
  const { data: document, isLoading, isError, refetch } = useDocument(documentId);
  const navigationState = (location.state || {}) as DocumentNavigationState;
  const resultIds = navigationState.resultIds || [];
  const currentResultIndex = resultIds.indexOf(documentId);
  const previousDocumentId = currentResultIndex > 0 ? resultIds[currentResultIndex - 1] : null;
  const nextDocumentId = currentResultIndex >= 0 && currentResultIndex < resultIds.length - 1
    ? resultIds[currentResultIndex + 1]
    : null;

  const handleReindex = async () => {
    setReindexing(true);
    try {
      await documentService.reindex(documentId);
      await refetch();
      toast({
        title: "Documento reindexado",
        description: "O documento foi reprocessado e o índice foi atualizado com sucesso (UC13).",
      });
    } catch {
      toast({
        title: "Falha na reindexação",
        description: "Não foi possível reindexar o documento.",
        variant: "destructive",
      });
    } finally {
      setReindexing(false);
    }
  };

  const handleDownload = async () => {
    if (!document?.downloadUrl) {
      toast({
        title: "Download indisponível",
        description: "Este documento não possui arquivo associado para recuperação.",
        variant: "destructive",
      });
      return;
    }

    setExporting("download");
    try {
      const { blob, filename } = await documentService.download(documentId);
      saveBlob(blob, filename || `${document.title}.${document.type.toLowerCase()}`);
    } catch {
      toast({
        title: "Falha no download",
        description: "Não foi possível baixar o arquivo original do documento.",
        variant: "destructive",
      });
    } finally {
      setExporting(null);
    }
  };

  const handleExport = async (format: "txt" | "json") => {
    setExporting(format);
    try {
      const { blob, filename } = await documentService.export(documentId, format);
      saveBlob(blob, filename || `${document?.title || "documento"}.${format}`);
    } catch {
      toast({
        title: "Falha na exportação",
        description: "Não foi possível exportar o conteúdo do documento.",
        variant: "destructive",
      });
    } finally {
      setExporting(null);
    }
  };

  const goToRelatedDocument = (targetId: number | null) => {
    if (!targetId) {
      return;
    }
    navigate(`/documento/${targetId}`, { state: navigationState });
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
        <Button
          variant="ghost"
          onClick={() => {
            if (navigationState.from) {
              navigate(`/resultados${navigationState.from}`);
              return;
            }
            navigate(-1);
          }}
          className="gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Voltar
        </Button>
        <div className="flex gap-2">
          {resultIds.length > 1 && (
            <div className="hidden sm:flex items-center gap-1 mr-2">
              <Button
                variant="outline"
                size="icon"
                disabled={!previousDocumentId}
                onClick={() => goToRelatedDocument(previousDocumentId)}
                title="Documento anterior dos resultados"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                disabled={!nextDocumentId}
                onClick={() => goToRelatedDocument(nextDocumentId)}
                title="Próximo documento dos resultados"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
          {isAdmin && (
            <Button
              variant="outline"
              className="gap-2"
              onClick={handleReindex}
              disabled={reindexing}
            >
              <RefreshCw className={`h-4 w-4 ${reindexing ? "animate-spin" : ""}`} />
              {reindexing ? "Reindexando..." : "Reindexar (Admin)"}
            </Button>
          )}
          <Button variant="outline" className="gap-2" onClick={() => handleExport("txt")} disabled={!!exporting}>
            <FileText className="h-4 w-4" />
            TXT
          </Button>
          <Button variant="outline" className="gap-2" onClick={() => handleExport("json")} disabled={!!exporting}>
            <FileJson className="h-4 w-4" />
            JSON
          </Button>
          <Button className="gap-2" onClick={handleDownload} disabled={!!exporting || !document.downloadUrl}>
            <Download className="h-4 w-4" />
            Original
          </Button>
        </div>
      </div>

      <div className="glass-card">
        {/* PDF Viewer Placeholder */}
          <div className="bg-muted/50 border-b border-border p-4 flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <FileText className="h-5 w-5" />
            Visualização completa do conteúdo extraído — {document.title}
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
              {document.documentType} · {document.format} · {document.size}
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
            <div className="flex items-center gap-2 text-muted-foreground">
              <FileText className="h-3.5 w-3.5" />
              {document.fileName}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <User className="h-3.5 w-3.5" />
              Enviado por {document.uploadedBy}
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm mt-3">
            <div className="flex items-center gap-2 text-muted-foreground">
              <FileText className="h-3.5 w-3.5" />
              {document.mimeType}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <FileText className="h-3.5 w-3.5" />
              {document.extractedCharacters} caracteres extraídos
            </div>
            <div className="flex min-w-0 items-center gap-2 text-muted-foreground">
              <Hash className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate" title={document.hash}>{document.hash}</span>
            </div>
            {currentResultIndex >= 0 && (
              <div className="flex items-center gap-2 text-muted-foreground">
                Resultado {currentResultIndex + 1} de {resultIds.length}
              </div>
            )}
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
