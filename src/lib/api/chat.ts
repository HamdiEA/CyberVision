// Client de chat frontend pour interroger le backend forensique.
// Utilitaire de chat utilisé par UploadResults pour poser des questions sur une image.
// Tente l'endpoint backend /chat ; bascule sur une réponse locale en cas d'échec.

import { buildApiUrl } from "@/lib/api/base";

export type AskImageQuestionParams = {
  question: string;
  imageUrl?: string;
  imageFile?: File; // Objet fichier transmis pour l'analyse visuelle
  analysis?: unknown;
};

export type AskImageQuestionResponse = {
  answer: string;
};

/** Convertir un fichier en chaîne base64 */
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // Extraire les données base64 après la virgule
      const base64 = result.includes(',') ? result.split(',')[1] : result;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Pose une question sur l'image avec contexte d'analyse et fallback local.
export async function askImageQuestion(params: AskImageQuestionParams): Promise<AskImageQuestionResponse> {
  const url = buildApiUrl("/chat");

  try {
    const requestBody: any = {
      question: params.question,
      imageUrl: params.imageUrl,
      analysis: params.analysis,
    };

    // Si un fichier est fourni, le convertir en base64 puis l'ajouter à la requête.
    if (params.imageFile) {
      try {
        requestBody.imageBase64 = await fileToBase64(params.imageFile);
        requestBody.imageMimeType = params.imageFile.type;
      } catch (err) {
        console.warn("Échec de conversion de l'image en base64", err);
      }
    }

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    });

    if (res.ok) {
      const data = (await res.json()) as Partial<AskImageQuestionResponse>;
      if (data?.answer) return { answer: data.answer };
    }
  } catch (err) {
    console.warn("Bascule de secours askImageQuestion", err);
  }

  // Message de secours pour ne pas bloquer l'interface si le chat backend est indisponible.
  return {
    answer:
      "Service de chat indisponible. Vérifiez que le backend est lancé et accessible via /chat.",
  };
}
