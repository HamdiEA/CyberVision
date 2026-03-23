/**
 * CyberVision API Service
 * Service pour communiquer avec le backend FastAPI
 */

import { API_BASE_URL, buildApiUrl } from "@/lib/api/base";

// Configuration de l'API
const API_TIMEOUT = 300000; // 5 minutes pour les analyses longues

// Types TypeScript
export interface AnalysisResult {
  success: boolean;
  error?: string;
  ai_interpretation?: string;
  filename: string;
  timestamp: string;
  integrity: {
    score: number;
    risk_level: 'safe' | 'warning' | 'suspect' | 'critical';
    confidence: number;
    summary: string;
    recommendations: string[];
  };
  modules: {
    exif: {
      has_exif: boolean;
      camera_info: Record<string, string>;
      date_info: Record<string, string>;
      anomalies: string[];
      risk_score: number;
    };
    structure: {
      file_format: string;
      dimensions: [number, number] | null;
      color_mode: string;
      is_corrupted: boolean;
      entropy: number;
      anomalies: string[];
      risk_score: number;
    };
    steganography: {
      suspicious: boolean;
      confidence: number;
      anomalies: string[];
      risk_score: number;
    };
    ai_visual: {
      authenticity: string;
      retouches_detected: boolean;
      retouches_details: string;
      visual_inconsistencies: string[];
      confidence_score: number;
      explanation: string;
      risk_score: number;
    };
  };
}

export interface ConfigResponse {
  max_file_size: number;
  allowed_extensions: string[];
  warnings: string[];
}

// Classe du service API
class APIService {
  private baseUrl: string;
  private timeout: number;

  // Normalise une erreur brute en message lisible.
  private toMessage(err: any, fallback: string) {
    if (!err) return fallback;
    if (typeof err === 'string') return err;
    if (err?.message && typeof err.message === 'string') return err.message;
    const candidate = err?.error ?? err?.detail ?? err?.msg ?? err?.statusText;
    if (typeof candidate === 'string') return candidate;
    try {
      return JSON.stringify(candidate || err);
    } catch {
      return fallback;
    }
  }

  constructor(baseUrl: string = API_BASE_URL, timeout: number = API_TIMEOUT) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }

  /**
   * Effectuer une requête HTTP avec timeout
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const isFormData = options.body instanceof FormData;
      const baseHeaders: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
      };
      if (isFormData && 'Content-Type' in baseHeaders) {
        // Laisser le navigateur définir automatiquement les limites multipart.
        delete (baseHeaders as any)['Content-Type'];
      }

      const response = await fetch(buildApiUrl(url), {
        ...options,
        signal: controller.signal,
        headers: baseHeaders,
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof TypeError) {
        throw new Error(
          "Impossible de joindre l'API backend. Démarrez le serveur backend sur le port 8000 ou configurez correctement VITE_API_URL."
        );
      }
      throw error;
    }
  }

  /**
   * Vérifier la santé de l'API
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.fetchWithTimeout('/health');
    return response.json();
  }

  /**
   * Obtenir la configuration de l'API
   */
  async getConfig(): Promise<ConfigResponse> {
    const response = await this.fetchWithTimeout('/config');
    return response.json();
  }

  /**
   * Analyser une image
   */
  async analyzeImage(
    file: File,
    token?: string
  ): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);

    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await this.fetchWithTimeout('/analyze', {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const message = this.toMessage(error, "Erreur lors de l'analyse");
      throw new Error(message);
    }

    return response.json();
  }

}

// Exporter une instance unique du service
export const apiService = new APIService();

// Exporter la classe pour les tests
export default APIService;