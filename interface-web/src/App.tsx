import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import LoginPage from "./pages/LoginPage";
import SearchPage from "./pages/SearchPage";
import ResultsPage from "./pages/ResultsPage";
import DocumentViewPage from "./pages/DocumentViewPage";
import IngestionPage from "./pages/IngestionPage";
import IndexStatusPage from "./pages/IndexStatusPage";
import MetricsPage from "./pages/MetricsPage";
import HistoryPage from "./pages/HistoryPage";
import UsersPage from "./pages/UsersPage";
import SettingsPage from "./pages/SettingsPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route element={<AppLayout />}>
            <Route path="/busca" element={<SearchPage />} />
            <Route path="/resultados" element={<ResultsPage />} />
            <Route path="/documento/:id" element={<DocumentViewPage />} />
            <Route path="/ingestao" element={<IngestionPage />} />
            <Route path="/indexacao" element={<IndexStatusPage />} />
            <Route path="/metricas" element={<MetricsPage />} />
            <Route path="/historico" element={<HistoryPage />} />
            <Route path="/usuarios" element={<UsersPage />} />
            <Route path="/configuracoes" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
