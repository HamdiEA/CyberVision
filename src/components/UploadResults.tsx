// Affichage detaille des resultats forensiques et du chat IA.
import { useEffect, useRef, useState } from "react";
import { askImageQuestion } from "@/lib/api/chat";
import { apiService, type AnalysisResult } from "@/services/api";

type Item = { name: string; url: string; file: File };

type Result = AnalysisResult | { error: string } | undefined;

type QaState = {
  question: string;
  answer?: string;
  loading?: boolean;
  error?: string;
};

const AUTO_FORENSIC_QUESTION =
  "À partir du rapport forensique, quel est le problème le plus probable dans cette image ? Donne un exemple concret de manipulation et une brève justification.";

const pickIntegrity = (raw: any) => raw?.integrity || raw?.integrity_score || {};
const pickModules = (raw: any) => raw?.modules || raw?.modules_results || {};
const riskLabel: Record<string, string> = {
  safe: "Faible",
  warning: "Moyen",
  suspect: "Élevé",
  critical: "Critique",
};

export default function UploadResults({ items }: { items: Item[] }) {
  const [results, setResults] = useState<Record<string, Result>>({});
  const [qa, setQa] = useState<Record<string, QaState>>({});
  const mounted = useRef(true);

  // Convertit toute erreur en message lisible pour l'UI.
  const toError = (e: any) => {
    if (typeof e === "string") return e;
    if (e?.message) return String(e.message);
    try {
      return JSON.stringify(e);
    } catch {
      return "Erreur inconnue";
    }
  };

  useEffect(() => {
    mounted.current = true;
    const run = async () => {
      const next: Record<string, Result> = {};
      const nextQa: Record<string, QaState> = {};
      for (const it of items) {
        try {
          const resp = await apiService.analyzeImage(it.file);
          if (!resp || !resp.modules || !resp.integrity) {
            throw new Error("Réponse d'analyse invalide");
          }
          console.info("Résultat d'analyse", { name: it.name, resp });
          next[it.name] = resp;
          nextQa[it.name] = {
            question: "",
            answer: resp.ai_interpretation,
          };

          if (!resp.ai_interpretation) {
            try {
              const aiResp = await askImageQuestion({
                question: AUTO_FORENSIC_QUESTION,
                imageUrl: it.url,
                imageFile: it.file,
                analysis: resp,
              });
              nextQa[it.name].answer = aiResp.answer;
            } catch {
              // Conserver le résultat forensique visible même si le post-traitement IA échoue.
            }
          }
        } catch (e: any) {
          next[it.name] = { error: toError(e) || "Analyse impossible" };
          nextQa[it.name] = { question: "" };
        }
      }
      if (mounted.current) setResults(next);
      if (mounted.current) setQa(nextQa);
    };
    run();
    return () => {
      mounted.current = false;
    };
  }, [items]);

  // Met a jour localement l'etat Q/R d'une image.
  const updateQa = (name: string, update: Partial<QaState>) => {
    setQa((prev) => ({ ...prev, [name]: { ...(prev[name] || { question: "" }), ...update } }));
  };

  // Envoie la question utilisateur au chat backend pour cette image.
  const handleAsk = async (name: string, imageUrl: string, imageFile?: File) => {
    const state = qa[name] || { question: "" };
    if (!state.question.trim()) return;
    updateQa(name, { loading: true, error: undefined, answer: undefined });
    try {
      const resp = await askImageQuestion({
        question: state.question,
        imageUrl,
        imageFile, // Transmettre le fichier image réel pour l'analyse visuelle.
        analysis: results[name] as any,
      });
      updateQa(name, { answer: resp.answer, loading: false });
    } catch (e: any) {
      updateQa(name, { error: toError(e) || "Impossible d'obtenir une réponse", loading: false });
    }
  };

  if (items.length === 0) return null;

  return (
    <div className="space-y-4">
      {items.map((it) => {
        const r = results[it.name];
        // Traiter comme analyse quand aucune erreur explicite n'est présente.
        const analysis = r && !(r as any)?.error ? (r as AnalysisResult) : undefined;
        const integrity = analysis ? pickIntegrity(analysis) : {};
        const modules = analysis ? pickModules(analysis) : {};
        const confidence = typeof integrity?.confidence === "number" ? integrity.confidence : 0;
        return (
          <div key={it.name} className="card flex gap-4 items-start">
            <div className="relative w-32 h-32 rounded-lg overflow-hidden bg-muted">
              <img src={it.url} alt={it.name} className="absolute inset-0 w-full h-full object-cover" />
            </div>
            <div className="flex-1 space-y-3 text-sm">
              <div className="font-medium" title={it.name}>{it.name}</div>
              {!r && <div className="text-muted-foreground">Analyse en cours...</div>}
              {r && "error" in r && <div className="text-destructive">{r.error}</div>}
              {(analysis || r) && (
                <div className="space-y-3">
                  {analysis && analysis.success === false && analysis.error && (
                    <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-xs">
                      {analysis.error}
                    </div>
                  )}
                  {!analysis && r && "error" in r && (
                    <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-xs">
                      {r.error}
                    </div>
                  )}
                  <div className="p-3 rounded-lg bg-primary/10 border border-primary/20">
                    <div className="font-semibold text-sm mb-1">Évaluation forensique</div>
                    <div className="text-xs text-muted-foreground flex flex-col gap-1">
                      <span>Score d'intégrité: <strong>{integrity?.score ?? '-'}</strong></span>
                      <span>Niveau de risque: <strong>{riskLabel[integrity?.risk_level] || integrity?.risk_level || '-'}</strong></span>
                      <span>Confiance: <strong>{confidence}%</strong></span>
                    </div>
                  </div>

                  {/* Résumé */}
                  <div>
                    <div className="text-xs font-semibold text-muted-foreground mb-1">Résumé</div>
                    <div className="text-sm text-foreground/90">{integrity?.summary || 'Résumé non disponible'}</div>
                  </div>

                  {/* EXIF */}
                  <div>
                    <div className="text-xs font-semibold text-muted-foreground mb-1">Anomalies EXIF</div>
                    <div className="text-xs text-foreground/90">
                      {modules?.exif?.anomalies?.length
                        ? modules.exif.anomalies.join("; ")
                        : "Aucune anomalie EXIF détectée"}
                    </div>
                  </div>

                  {/* Structure */}
                  <div>
                    <div className="text-xs font-semibold text-muted-foreground mb-1">Structure</div>
                    <div className="text-xs text-foreground/90">
                      {modules?.structure?.file_format || "Format inconnu"}
                      {modules?.structure?.anomalies?.length ? ` — ${modules.structure.anomalies.join('; ')}` : ""}
                    </div>
                  </div>

                  {/* Stéganographie */}
                  <div>
                    <div className="text-xs font-semibold text-muted-foreground mb-1">Stéganographie</div>
                    <div className="text-xs text-foreground/90">
                      {modules?.steganography?.suspicious ? "Signes de données cachées" : "Pas d'indicateurs évidents"}
                    </div>
                  </div>

                  {/* Analyse visuelle */}
                  <div>
                    <div className="text-xs font-semibold text-muted-foreground mb-1">Analyse visuelle</div>
                    <div className="text-xs text-foreground/90">
                      {modules?.ai_visual?.explanation || "Pas d'explication disponible"}
                    </div>
                  </div>

                  {/* Recommandations */}
                  {integrity?.recommendations && integrity.recommendations.length > 0 && (
                    <div>
                      <div className="text-xs font-semibold text-muted-foreground mb-2">Recommandations</div>
                      <ul className="text-xs space-y-1 list-disc list-inside">
                        {integrity.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {qa[it.name]?.answer && (
                    <div className="rounded-lg border border-primary/30 bg-primary/5 p-3">
                      <div className="text-xs font-semibold text-muted-foreground mb-1">Interprétation IA forensique</div>
                      <div className="text-xs leading-relaxed">{qa[it.name]?.answer}</div>
                    </div>
                  )}
                </div>
              )}

              {analysis && (
                <div className="space-y-2">
                  <label className="text-xs text-muted-foreground">Posez une question sur cette image</label>
                  <textarea
                    value={qa[it.name]?.question || ""}
                    onChange={(e) => updateQa(it.name, { question: e.target.value })}
                    rows={2}
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs focus:border-primary focus:ring-0"
                    placeholder="Ex: Y a-t-il des signes de manipulation dans cette image ?"
                  />
                  <div className="flex items-center gap-2">
                    <button
                      className="btn-primary text-xs"
                      disabled={qa[it.name]?.loading || !(qa[it.name]?.question || "").trim()}
                      onClick={() => handleAsk(it.name, it.url, it.file)}
                    >
                      {qa[it.name]?.loading ? "Consultation de l'IA..." : "Poser à l'IA"}
                    </button>
                    {qa[it.name]?.error && <span className="text-destructive text-xs">{qa[it.name]?.error}</span>}
                  </div>
                </div>
              )}

              {analysis && (
                <details className="text-xs text-muted-foreground/80">
                  <summary>Données brutes</summary>
                  <pre className="mt-1 whitespace-pre-wrap break-words bg-muted/40 p-2 rounded">{JSON.stringify(analysis, null, 2)}</pre>
                </details>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
