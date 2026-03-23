// Section hero de presentation du produit.
import { useLanguage, translations } from "@/hooks/useLanguage";

// Affiche l'accroche principale et les appels a l'action.
export default function Hero() {
  const { language } = useLanguage();
  const t = translations[language];

  return (
    <section className="relative py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent pointer-events-none" />
      
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-primary/50 to-transparent animate-pulse" />
      <div className="absolute top-12 left-0 right-0 h-px bg-gradient-to-r from-primary/30 via-primary/10 to-transparent" />
      <div className="absolute top-24 left-0 right-0 h-px bg-gradient-to-r from-primary/20 to-transparent" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="flex justify-center">
            <div className="group relative h-52 w-52 md:h-64 md:w-64">
              <img
                src="/LOGO.png"
                alt="Logo CyberVision"
                className="absolute inset-0 h-full w-full scale-[1.9] md:scale-[2.1] object-contain drop-shadow-2xl"
              />
            </div>
          </div>

          <div className="space-y-4">
            <h1 className="text-6xl md:text-7xl font-bold leading-tight">
              <span className="bg-gradient-to-r from-primary via-destructive to-primary bg-clip-text text-transparent">
                {t.forensicAnalysis}
              </span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              {t.platformDescription}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <a 
              href="/upload" 
              className="px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2"
            >
              {t.analyzeImage}
            </a>
            <a 
              href="/how-to-use" 
              className="px-8 py-3 border border-foreground text-foreground font-semibold rounded-lg hover:bg-foreground/5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-foreground/50 focus:ring-offset-2"
            >
              {t.viewDocumentation}
            </a>
          </div>
        </div>

      </div>
    </section>
  );
}
