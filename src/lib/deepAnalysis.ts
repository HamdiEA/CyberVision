// Appels frontend vers l'analyse forensique avancee.
import { API_BASE_URL, buildApiUrl } from "@/lib/api/base";

export const DEEP_ANALYSIS_API =
  (import.meta.env.VITE_ANALYSIS_API_URL as string | undefined)?.trim() || API_BASE_URL;

// Envoie un fichier au backend et retourne le resultat d'analyse avancee.
export async function deepAnalyzeFile(file: File) {
  const form = new FormData();
  // Aligner avec le backend /analyze qui attend le champ "file".
  form.append('file', file);
  let res: Response;
  try {
    const endpoint = DEEP_ANALYSIS_API === API_BASE_URL
      ? buildApiUrl('/analyze')
      : `${DEEP_ANALYSIS_API.replace(/\/$/, '')}/analyze`;
    res = await fetch(endpoint, {
      method: 'POST',
      body: form,
    });
  } catch {
    throw new Error('Impossible de joindre le backend d\'analyse. Démarrez le backend ou configurez VITE_API_URL.');
  }
  if (!res.ok) throw new Error(`Échec de l'analyse avancée: ${res.status}`);
  return res.json();
}
