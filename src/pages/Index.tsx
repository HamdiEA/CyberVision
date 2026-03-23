// Page d'accueil avec presentation de la plateforme.
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import { useLanguage, translations } from "@/hooks/useLanguage";

// Assemble les sections principales de la home.
const Index = () => {
  const { language } = useLanguage();
  const t = translations[language];
  return (
    <div className="min-h-screen bg-background cyber-grid-bg relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-primary/50 to-transparent" />
      <div className="absolute top-12 left-0 right-0 h-px bg-gradient-to-r from-primary/30 via-primary/10 to-transparent" />
      <div className="absolute top-24 left-0 right-0 h-px bg-gradient-to-r from-primary/20 to-transparent" />
      
      <Header />
      <Hero />
      <Features />

      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center space-y-4">
            <h2 className="text-3xl md:text-4xl font-bold">{t.howItWorks}</h2>
            <p className="text-lg text-muted-foreground">
              {t.uploadDescription}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mt-12 text-left">
            {[
              {
                title: t.preprocessing,
                body: t.preprocessingDesc,
                accent: "bg-primary/15 text-primary",
                index: 1,
              },
              {
                title: t.detection,
                body: t.detectionDesc,
                accent: "bg-secondary/15 text-secondary",
                index: 2,
              },
              {
                title: t.reporting,
                body: t.reportingDesc,
                accent: "bg-accent/15 text-accent",
                index: 3,
              },
            ].map((item) => (
              <div key={item.title} className="card space-y-3">
                <div className={`h-12 w-12 rounded-full flex items-center justify-center font-bold ${item.accent}`}>
                  {item.index}
                </div>
                <h3 className="font-semibold text-lg">{item.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
