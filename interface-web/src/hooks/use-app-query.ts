import { useQuery } from "@tanstack/react-query";
import {
  documentService,
  historyService,
  indexService,
  ingestionService,
  metricsService,
  searchService,
  settingsService,
  userService,
} from "@/lib/api/services";
import type { SearchFilters } from "@/types/app";

export const useRecentSearches = () =>
  useQuery({
    queryKey: ["recent-searches"],
    queryFn: () => searchService.recentSearches(),
  });

export const useSearchResults = (query: string, filters: SearchFilters) =>
  useQuery({
    queryKey: ["search-results", query, filters],
    queryFn: () => searchService.search(query, filters),
    enabled: !!query.trim(),
  });

export const useDocument = (id: number) =>
  useQuery({
    queryKey: ["document", id],
    queryFn: () => documentService.getById(id),
    enabled: Number.isFinite(id),
  });

export const useUsers = () =>
  useQuery({
    queryKey: ["users"],
    queryFn: () => userService.list(),
  });

export const useIngestionBatch = () =>
  useQuery({
    queryKey: ["ingestion-batch"],
    queryFn: () => ingestionService.batchFiles(),
  });

export const useIngestionHistory = () =>
  useQuery({
    queryKey: ["ingestion-history"],
    queryFn: () => ingestionService.history(),
  });

export const useIndexStatus = () =>
  useQuery({
    queryKey: ["index-status"],
    queryFn: () => indexService.status(),
    refetchInterval: 30000,
  });

export const useMetrics = () =>
  useQuery({
    queryKey: ["metrics"],
    queryFn: () => metricsService.snapshot(),
  });

export const useHistory = () =>
  useQuery({
    queryKey: ["history"],
    queryFn: () => historyService.list(),
  });

export const useSettings = () =>
  useQuery({
    queryKey: ["settings"],
    queryFn: () => settingsService.get(),
  });
