// Zone d'upload et declenchement des analyses forensiques.
import { useCallback, useState, type DragEvent, type ChangeEvent } from "react";
import { Upload, X, FileImage } from "lucide-react";
import UploadResults from "@/components/UploadResults";
import { deepAnalyzeFile, DEEP_ANALYSIS_API } from "@/lib/deepAnalysis";
import { useLanguage, translations } from "@/hooks/useLanguage";
// Utilisation de styles de boutons simples pour éviter les problèmes d'affichage.

const UploadZone = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [toAnalyze, setToAnalyze] = useState<{ name: string; url: string; file: File }[]>([]);
  const [deepResult, setDeepResult] = useState<any | null>(null);
  const [deepLoading, setDeepLoading] = useState(false);

  // Gere l'etat visuel du drag and drop.
  const handleDrag = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  // Recupere l'image deposee et prepare l'analyse.
  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      const droppedImage = Array.from(e.dataTransfer.files).find((file) => file.type.startsWith("image/"));
      if (droppedImage) {
        setSelectedFile(droppedImage);
        setToAnalyze([]);
        setDeepResult(null);
        setMessage(
          "1 image sélectionnée. La plateforme analyse une seule image par envoi."
        );
      } else {
        setMessage("Déposez un fichier image valide.");
      }
    },
    []
  );

  // Lit l'image choisie depuis l'input fichier.
  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const picked = e.target.files[0];
      if (!picked) return;
      setSelectedFile(picked);
      setToAnalyze([]);
      setDeepResult(null);
      setMessage(
        "Image prête pour l'analyse forensique."
      );
    }
  };

  // Reinitialise l'image et les resultats affiches.
  const clearSelectedImage = () => {
    setSelectedFile(null);
    setToAnalyze([]);
    setDeepResult(null);
  };

  // Lance l'analyse forensique standard.
  const handleAnalyze = () => {
    if (!selectedFile) {
      setMessage("Ajoutez une image pour commencer l'analyse forensique.");
      return;
    }
    const items = [{ name: selectedFile.name, url: URL.createObjectURL(selectedFile), file: selectedFile }];
    setToAnalyze(items);
    setMessage("Exécution de l'analyse forensique sur 1 image...");
  };

  // Lance l'analyse avancee cote serveur.
  const handleDeepAnalyze = async () => {
    if (!DEEP_ANALYSIS_API) {
      setMessage("Configurez VITE_ANALYSIS_API_URL pour activer l'analyse forensique avancée.");
      return;
    }
    if (!selectedFile) {
      setMessage("Ajoutez une image pour une analyse forensique avancée.");
      return;
    }
    setDeepLoading(true);
    setDeepResult(null);
    try {
      const res = await deepAnalyzeFile(selectedFile);
      setDeepResult(res);
      setMessage("Analyse forensique avancée terminée.");
    } catch (e: any) {
      setMessage(e?.message || "Analyse forensique avancée échouée");
    } finally {
      setDeepLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div
        className={`card border-2 border-dashed transition-all ${
          dragActive ? "border-primary bg-primary/5 scale-[1.01]" : "border-white/15"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="p-10 text-center space-y-4">
          <div className="flex justify-center">
            <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center">
              <Upload className="h-10 w-10 text-primary" />
            </div>
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">{t.uploadEvidence}</h3>
            <p className="text-muted-foreground">{t.uploadPlaceholder}</p>
          </div>

          <input type="file" accept="image/*" onChange={handleFileInput} className="hidden" id="file-upload" />
          <label htmlFor="file-upload" className="inline-flex items-center justify-center">
            <span className="btn-primary cursor-pointer">
              <FileImage className="h-4 w-4" />
              {t.selectImages}
            </span>
          </label>

          <p className="text-xs text-muted-foreground">Formats: JPG, PNG, TIFF - Limite: 1 image</p>
          {message && <div className="text-sm text-foreground/80">{message}</div>}
        </div>
      </div>

      {selectedFile && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold">{t.selectedImages} (1)</h4>
            <button
              className="btn-ghost text-sm"
              onClick={clearSelectedImage}
            >
              {t.clearAll}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="relative group rounded-lg overflow-hidden bg-muted aspect-square max-w-sm">
                <img src={URL.createObjectURL(selectedFile)} alt={selectedFile.name} className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-background/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <button className="btn-ghost text-xs" onClick={clearSelectedImage}>
                    <X className="h-4 w-4" />
                    {t.removeImage}
                  </button>
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-background/90 to-transparent">
                  <p className="text-xs truncate">{selectedFile.name}</p>
                </div>
              </div>
          </div>

          <button className="btn-primary w-full" onClick={handleAnalyze}>{t.startForensicAnalysis}</button>
          {DEEP_ANALYSIS_API && (
            <button className="btn-ghost w-full" onClick={handleDeepAnalyze} disabled={deepLoading}>
              {deepLoading ? t.searching : t.advancedAnalysis}
            </button>
          )}

          {toAnalyze.length > 0 && (
            <div className="pt-4 space-y-2">
              <h4 className="font-semibold">{t.analysisResults}</h4>
              <UploadResults items={toAnalyze} />
            </div>
          )}
          {deepResult && (
            <div className="pt-4 space-y-2">
              <h4 className="font-semibold">{t.advancedResults}</h4>
              <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-80">{JSON.stringify(deepResult, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadZone;
