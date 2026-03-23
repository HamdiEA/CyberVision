// Page d'analyse: upload, execution et lecture des resultats.
import Header from "@/components/Header";
import UploadZone from "@/components/UploadZone";
import { AlertTriangle } from "lucide-react";
import { useLanguage, translations } from "@/hooks/useLanguage";

// Affiche le parcours d'analyse forensique utilisateur.
const Upload = () => {
  const { language } = useLanguage();
  const t = translations[language];

  const steps = [
    t.uploadEvidence,
    t.anomaliesDetected,
    t.forensicResults,
  ];

  return (
    <div className="min-h-screen bg-background cyber-grid-bg relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-primary/50 to-transparent" />
      <div className="absolute top-12 left-0 right-0 h-px bg-gradient-to-r from-primary/30 via-primary/10 to-transparent" />
      <div className="absolute top-24 left-0 right-0 h-px bg-gradient-to-r from-primary/20 to-transparent" />
      <Header />
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12 space-y-4">
            <div className="pill inline-flex items-center justify-center gap-2">
              <AlertTriangle className="h-4 w-4 text-primary" />
              <span>{t.realtimeAnalysis}</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold">{t.analyzeEvidence}</h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {t.uploadDescription}
            </p>
          </div>

          <UploadZone />

          <div className="mt-12 grid md:grid-cols-3 gap-6">
            {steps.map((label, idx) => (
              <div key={label} className="card text-center space-y-2">
                <div className="text-3xl font-bold text-primary">{idx + 1}</div>
                <p className="text-sm text-muted-foreground">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Upload;
