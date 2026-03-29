export type UserRole = "Administrador" | "Usuário";

export type UserSummary = {
  id: number;
  name: string;
  login: string;
  email: string;
  role: UserRole;
  active: boolean;
};

export type SessionUser = UserSummary & {
  token: string;
};

export type SearchFilters = {
  category?: string;
  documentType?: string;
  dateFrom?: string;
  dateTo?: string;
  sortBy?: string;
  limit?: number;
  page?: number;
};

export type SearchResult = {
  id: number;
  title: string;
  snippet: string;
  category: string;
  type: string;
  date: string;
  relevance: number;
};

export type SearchResponse = {
  query: string;
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
  items: SearchResult[];
};

export type SearchHistoryItem = {
  id: number;
  term: string;
};

export type DocumentDetails = {
  id: number;
  title: string;
  category: string;
  type: string;
  date: string;
  author: string;
  format: string;
  pages: number;
  version: number;
  indexedAt: string;
  size: string;
  downloadUrl?: string;
  content: string;
  extractedCharacters: number;
};

export type IngestionBatchFile = {
  name: string;
  size: string;
  status: "validated" | "indexed" | "error";
};

export type IngestionHistoryEntry = {
  date: string;
  file: string;
  type: string;
  result: string;
  details: string;
};

export type DocumentUploadPayload = {
  file: File;
  category: string;
  documentDate?: string;
};

export type BatchUploadPayload = {
  files: File[];
  category: string;
  documentDate?: string;
};

export type UploadedDocument = {
  id: number;
  title: string;
  fileName: string;
  category: string;
  type: string;
  mimeType: string;
  sizeBytes: number;
  sizeLabel: string;
  date: string | null;
  uploadedAt: string;
  validated: boolean;
  integrityOk: boolean;
  hash: string;
  extracted: boolean;
  extractedCharacters: number;
};

export type BatchUploadItem = {
  fileName: string;
  status: "indexed" | "error";
  message: string;
  documentId?: number | null;
  extractedCharacters: number;
  sizeLabel?: string | null;
};

export type BatchUploadResult = {
  totalFiles: number;
  successCount: number;
  failureCount: number;
  items: BatchUploadItem[];
};

export type IndexLogEntry = {
  time: string;
  message: string;
  type: "info" | "success" | "error";
};

export type IndexStatusSnapshot = {
  indexedDocuments: number;
  averageTime: string;
  successRate: string;
  errors: number;
  currentProgress: number;
  remainingEstimate: string;
  summary: {
    completed: number;
    processing: number;
    failed: number;
  };
  logs: IndexLogEntry[];
};

export type MetricsOverview = {
  totalQueries: number;
  averageSearchTime: string;
  indexedDocuments: number;
  successRate: string;
  averageResults: number;
  queriesToday: number;
};

export type MetricsPoint = {
  day: string;
  consultas: number;
};

export type NamedValue = {
  name: string;
  value: number;
};

export type MetricsSnapshot = {
  overview: MetricsOverview;
  queriesByDay: MetricsPoint[];
  topTerms: NamedValue[];
  documentsByCategory: NamedValue[];
};

export type HistoryEntry = {
  date: string;
  user: string;
  action: string;
  details: string;
  status: "success" | "error" | "info" | "warning";
};

export type AppSettings = {
  instanceName: string;
  apiBaseUrl: string;
  autoIndexing: boolean;
  ocrEnabled: boolean;
  maxFileSizeMb: number;
  emailNotifications: boolean;
  weeklyReport: boolean;
};
