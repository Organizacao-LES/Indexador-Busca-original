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
  BatchUploadPayload,
  BatchUploadResult,
  DocumentDetails,
  DocumentUploadPayload,
  HistoryEntry,
  IndexStatusSnapshot,
  IngestionBatchFile,
  IngestionHistoryEntry,
  MetricsSnapshot,
  SearchFilters,
  SearchHistoryItem,
  SearchResponse,
  SessionUser,
  UploadedDocument,
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

type BackendUser = {
  cod_usuario: number;
  nome: string;
  login: string;
  email: string;
  perfil: "ADMIN" | "USER";
  ativo: boolean;
};

type BackendUserPayload = {
  nome?: string;
  login?: string;
  email?: string;
  perfil?: "ADMIN" | "USER";
  ativo?: boolean;
  senha?: string;
};

const mapBackendRole = (perfil: BackendUser["perfil"]): UserSummary["role"] =>
  perfil === "ADMIN" ? "Administrador" : "Usuário";

const mapUser = (user: BackendUser): UserSummary => ({
  id: user.cod_usuario,
  name: user.nome,
  login: user.login,
  email: user.email,
  role: mapBackendRole(user.perfil),
  active: user.ativo,
});

type BackendSessionUser = {
  id?: number;
  cod_usuario?: number;
  name?: string;
  nome?: string;
  login: string;
  email: string;
  role?: string;
  perfil?: "ADMIN" | "USER";
  active?: boolean;
  ativo?: boolean;
  token?: string;
  access_token?: string;
};

const mapSessionRole = (role?: string, perfil?: BackendSessionUser["perfil"]): SessionUser["role"] => {
  if (role === "Administrador" || perfil === "ADMIN" || role === "ADMIN") {
    return "Administrador";
  }
  return "Usuário";
};

const mapSessionUser = (session: BackendSessionUser): SessionUser => ({
  id: session.id ?? session.cod_usuario ?? 0,
  name: session.name ?? session.nome ?? session.login,
  login: session.login,
  email: session.email,
  role: mapSessionRole(session.role, session.perfil),
  active: session.active ?? session.ativo ?? true,
  token: session.token ?? session.access_token ?? "",
});

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

    const session = await apiRequest<BackendSessionUser>("/api/v1/auth/login", {
      method: "POST",
      body: { email, password },
    });
    return mapSessionUser(session);
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

    const users = await apiRequest<BackendUser[]>("/api/v1/users/");
    return users.map(mapUser);
  },

  async create(payload: {
    name: string;
    login: string;
    email: string;
    password: string;
    role: UserSummary["role"];
  }): Promise<UserSummary> {
    const body: BackendUserPayload = {
      nome: payload.name,
      login: payload.login,
      email: payload.email,
      senha: payload.password,
      perfil: payload.role === "Administrador" ? "ADMIN" : "USER",
      ativo: true,
    };
    const created = await apiRequest<BackendUser>("/api/v1/users/", {
      method: "POST",
      body,
    });
    return mapUser(created);
  },

  async update(
    id: number,
    payload: {
      name: string;
      login: string;
      email: string;
      role: UserSummary["role"];
    },
  ): Promise<UserSummary> {
    const body: BackendUserPayload = {
      nome: payload.name,
      login: payload.login,
      email: payload.email,
      perfil: payload.role === "Administrador" ? "ADMIN" : "USER",
    };
    const updated = await apiRequest<BackendUser>(`/api/v1/users/${id}`, {
      method: "PUT",
      body,
    });
    return mapUser(updated);
  },

  async toggleActive(id: number, active: boolean): Promise<UserSummary> {
    const updated = await apiRequest<BackendUser>(`/api/v1/users/${id}`, {
      method: "PUT",
      body: { ativo: active },
    });
    return mapUser(updated);
  },
};

export const ingestionService = {
  async uploadDocument(payload: DocumentUploadPayload): Promise<UploadedDocument> {
    if (shouldUseMocks()) {
      await delay(500);
      return {
        id: Date.now(),
        title: payload.file.name.replace(/\.[^.]+$/, ""),
        fileName: payload.file.name,
        category: payload.category,
        type: payload.file.name.split(".").pop()?.toUpperCase() || "TXT",
        mimeType: payload.file.type || "application/octet-stream",
        sizeBytes: payload.file.size,
        sizeLabel: `${(payload.file.size / 1024 / 1024).toFixed(1)} MB`,
        date: payload.documentDate || null,
        uploadedAt: new Date().toISOString(),
        validated: true,
        integrityOk: true,
        hash: "mock-hash",
        extracted: true,
        extractedCharacters: 1200,
      };
    }

    const formData = new FormData();
    formData.append("file", payload.file);
    formData.append("category", payload.category);
    if (payload.documentDate) {
      formData.append("document_date", payload.documentDate);
    }

    return apiRequest<UploadedDocument>("/api/v1/ingestion/upload", {
      method: "POST",
      body: formData,
    });
  },

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

  async uploadBatch(payload: BatchUploadPayload): Promise<BatchUploadResult> {
    if (shouldUseMocks()) {
      await delay(700);
      return {
        totalFiles: payload.files.length,
        successCount: payload.files.length,
        failureCount: 0,
        items: payload.files.map((file, index) => ({
          fileName: file.name,
          status: "indexed",
          message: "Documento validado, extraído e armazenado com sucesso.",
          documentId: Date.now() + index,
          extractedCharacters: 1200,
          sizeLabel: `${(file.size / 1024 / 1024).toFixed(1)} MB`,
        })),
      };
    }

    const formData = new FormData();
    payload.files.forEach((file) => formData.append("files", file));
    formData.append("category", payload.category);
    if (payload.documentDate) {
      formData.append("document_date", payload.documentDate);
    }

    return apiRequest<BatchUploadResult>("/api/v1/ingestion/upload-batch", {
      method: "POST",
      body: formData,
    });
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
