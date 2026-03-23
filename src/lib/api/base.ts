// Base URL API et helpers de construction d'URL.
const normalizeBaseUrl = (raw?: string): string => {
  const value = (raw || "").trim();
  if (!value) return "/api";
  return value.replace(/\/$/, "");
};

export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_URL as string | undefined);

// Construit une URL API a partir d'un chemin relatif.
export const buildApiUrl = (path: string): string => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};
