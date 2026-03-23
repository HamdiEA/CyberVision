// Guide d'utilisation pas a pas de CyberVision.
import Header from "@/components/Header";
import { Link } from "react-router-dom";

const steps = [
  {
    title: "1. Préparer l'image",
    description:
      "Utilisez une image nette (JPG, PNG ou TIFF), idéalement non recadrée et non recompressée plusieurs fois, afin de conserver un maximum d'indices forensiques.",
  },
  {
    title: "2. Importer l'image",
    description:
      "Accédez à la page d'analyse, glissez-déposez une image ou sélectionnez-la via le bouton. CyberVision traite une image par envoi pour une lecture claire des résultats.",
  },
  {
    title: "3. Lancer l'analyse forensique",
    description:
      "Cliquez sur 'Commencer l'analyse forensique'. Le backend exécute l'analyse EXIF, structurelle, stéganographique et visuelle, puis calcule un score global.",
  },
  {
    title: "4. Lire les résultats",
    description:
      "Consultez le score d'intégrité, le niveau de risque, le résumé, les anomalies EXIF, la structure du fichier, les indices de stéganographie et l'explication visuelle IA.",
  },
  {
    title: "5. Interroger l'IA",
    description:
      "Utilisez la zone 'Poser à l'IA' pour demander des précisions ciblées: zones suspectes, type de manipulation probable, niveau de confiance, ou recommandations d'audit.",
  },
  {
    title: "6. Prendre une décision",
    description:
      "Recoupez toujours les conclusions avec le contexte métier. Un résultat forensique est un indicateur technique d'aide à la décision, pas une preuve unique absolue.",
  },
];

// Affiche les etapes et bonnes pratiques d'analyse.
export default function HowToUse() {
  return (
    <div className="min-h-screen bg-background cyber-grid-bg relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-primary/50 to-transparent" />
      <div className="absolute top-12 left-0 right-0 h-px bg-gradient-to-r from-primary/30 via-primary/10 to-transparent" />
      <div className="absolute top-24 left-0 right-0 h-px bg-gradient-to-r from-primary/20 to-transparent" />

      <Header />

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold">Comment utiliser CyberVision</h1>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Guide rapide pour obtenir une analyse forensique fiable, comprendre les indicateurs,
              et exploiter correctement les réponses IA.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            {steps.map((step) => (
              <article key={step.title} className="rounded-xl border border-border/40 bg-card/80 p-5 space-y-2 shadow-sm">
                <h2 className="text-lg font-semibold">{step.title}</h2>
                <p className="text-sm text-muted-foreground leading-relaxed">{step.description}</p>
              </article>
            ))}
          </div>

          <section className="rounded-xl border border-primary/30 bg-primary/5 p-6 space-y-3">
            <h2 className="text-xl font-semibold">Bonnes pratiques</h2>
            <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
              <li>Évitez les captures d'écran: préférez le fichier source original.</li>
              <li>Comparez, si possible, plusieurs versions de la même image.</li>
              <li>Conservez un historique des analyses pour tracer les décisions.</li>
              <li>En cas de risque élevé, réalisez une vérification manuelle complémentaire.</li>
            </ul>
          </section>

          <div className="flex flex-wrap justify-center gap-3 pt-2">
            <Link
              to="/upload"
              className="px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors"
            >
              Commencer l'analyse
            </Link>
            <Link
              to="/"
              className="px-6 py-3 rounded-lg border border-border/60 text-foreground hover:bg-muted transition-colors"
            >
              Retour à l'accueil
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
