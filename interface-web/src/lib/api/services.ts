import { apiRequest } from "@/lib/api/client";
import {
  defaultSettings,
  mockBatchFiles,
  mockDocuments,
  mockHistory,
  mockIndexStatus,
  mockIngestionHistory,
  mockMetrics,
  mockRecentSearches,
  mockSearch,
  mockSessionUser,
  mockUsers,
} from "@/lib/api/mock-data";
import { appEnv } from "@/lib/env";
import { storageKeys } from "@/lib/storage";
import type {
  AppSettings,
  DocumentDetails,
  HistoryEntry,
  IndexStatusSnapshot,
  IngestionBatchFile,
  IngestionHistoryEntry,
  MetricsSnapshot,
  SearchFilters,
  SearchHistoryItem,
  SearchResponse,
  SessionUser,
  UserSummary,
} from "@/types/app";

const delay = (ms = 350) => new Promise((resolve) => setTimeout(resolve, ms));

const shouldUseMocks = () => appEnv.useMockApi;

const readStoredSettings = (): AppSettings => {
  const value = localStorage.getItem(storageKeys.settings);
  if (!value) {
    return { ...defaultSettings, apiBaseUrl: appEnv.apiBaseUrl };
  }

  try {
    return JSON.parse(value) as AppSettings;
  } catch {
    return { ...defaultSettings, apiBaseUrl: appEnv.apiBaseUrl };
  }
};

const persistSettings = (settings: AppSettings) => {
  localStorage.setItem(storageKeys.settings, JSON.stringify(settings));
};

export const authService = {
  async login(email: string, password: string): Promise<SessionUser> {
    if (shouldUseMocks()) {
      await delay();
      if (!email || !password) {
        throw new Error("Informe e-mail e senha.");
      }

      return {
        ...mockSessionUser,
        email,
      };
    }

    return apiRequest<SessionUser>("/api/v1/auth/login", {
      method: "POST",
      body: { email, password },
    });
  },
};

export const searchService = {
  async search(query: string, filters: SearchFilters = {}): Promise<SearchResponse> {
    if (shouldUseMocks()) {
      await delay();
      return mockSearch(query, filters.page, filters.limit);
    }

    return apiRequest<SearchResponse>("/api/v1/search", {
      query: {
        q: query,
        category: filters.category,
        documentType: filters.documentType,
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
        sortBy: filters.sortBy,
        limit: filters.limit,
        page: filters.page,
      },
    });
  },

  async recentSearches(): Promise<SearchHistoryItem[]> {
    if (shouldUseMocks()) {
      await delay(150);
      return mockRecentSearches;
    }

    return apiRequest<SearchHistoryItem[]>("/api/v1/search/history");
  },
};

export const documentService = {
  async getById(id: number): Promise<DocumentDetails> {
    if (shouldUseMocks()) {
      await delay();
      const document = mockDocuments.find((item) => item.id === id);
      if (!document) {
        throw new Error("Documento não encontrado.");
      }
      return document;
    }

    return apiRequest<DocumentDetails>(`/api/v1/documents/${id}`);
  },

  async reindex(id: number): Promise<void> {
    if (shouldUseMocks()) {
      await delay(800);
      return;
    }

    return apiRequest<void>(`/api/v1/documents/${id}/reindex`, {
      method: "POST",
    });
  },
};

export const userService = {
  async list(): Promise<UserSummary[]> {
    if (shouldUseMocks()) {
      await delay();
      return mockUsers;
    }

    return apiRequest<UserSummary[]>("/api/v1/users");
  },
};

export const ingestionService = {
  async batchFiles(): Promise<IngestionBatchFile[]> {
    if (shouldUseMocks()) {
      await delay(150);
      return mockBatchFiles;
    }

    return apiRequest<IngestionBatchFile[]>("/api/v1/ingestion/batch");
  },

  async history(): Promise<IngestionHistoryEntry[]> {
    if (shouldUseMocks()) {
      await delay(150);
      return mockIngestionHistory;
    }

    return apiRequest<IngestionHistoryEntry[]>("/api/v1/ingestion/history");
  },
};

export const indexService = {
  async status(): Promise<IndexStatusSnapshot> {
    if (shouldUseMocks()) {
      await delay(200);
      return mockIndexStatus;
    }

    return apiRequest<IndexStatusSnapshot>("/api/v1/index/status");
  },
};

export const metricsService = {
  async snapshot(): Promise<MetricsSnapshot> {
    if (shouldUseMocks()) {
      await delay(200);
      return mockMetrics;
    }

    return apiRequest<MetricsSnapshot>("/api/v1/metrics");
  },
};

export const historyService = {
  async list(): Promise<HistoryEntry[]> {
    if (shouldUseMocks()) {
      await delay(150);
      return mockHistory;
    }

    return apiRequest<HistoryEntry[]>("/api/v1/history");
  },
};

export const settingsService = {
  async get(): Promise<AppSettings> {
    if (shouldUseMocks()) {
      await delay(100);
      return readStoredSettings();
    }

    return apiRequest<AppSettings>("/api/v1/settings");
  },

  async update(settings: AppSettings): Promise<AppSettings> {
    if (shouldUseMocks()) {
      await delay(250);
      persistSettings(settings);
      return settings;
    }

    return apiRequest<AppSettings>("/api/v1/settings", {
      method: "PUT",
      body: settings,
    });
  },
};
