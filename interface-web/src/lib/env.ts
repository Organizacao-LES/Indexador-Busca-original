const parseBoolean = (value: string | undefined, fallback: boolean) => {
  if (value === undefined) {
    return fallback;
  }

  return value === "true";
};

export const appEnv = {
  apiBaseUrl: import.meta.env.VITE_API_URL || "http://localhost:8000",
  useMockApi: parseBoolean(import.meta.env.VITE_USE_MOCK_API, true),
  appName: import.meta.env.VITE_APP_NAME || "IFESDOC",
};
