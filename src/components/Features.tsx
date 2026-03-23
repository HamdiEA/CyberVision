// Bloc des fonctionnalites cles de la plateforme.
import { Brain, Zap, Shield, Database } from "lucide-react";
import { useLanguage, translations } from "@/hooks/useLanguage";

// Presente les capacites forensiques principales.
const Features = () => {
  const { language } = useLanguage();
  const t = translations[language];

  const features = [
    {
      icon: Brain,
      title: t.advancedAiDetection,
      description: t.advancedAiDesc,
    },
    {
      icon: Zap,
      title: t.realtimeAnalysis,
      description: t.realtimeDesc,
    },
    {
      icon: Shield,
      title: t.multiLayerSecurity,
      description: t.multiLayerSecurityDesc,
    },
    {
      icon: Database,
      title: t.comprehensiveReporting,
      description: t.comprehensiveReportingDesc,
    },
  ];

  return (
    <section className="py-32 relative overflow-hidden">
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
            {t.coreCapabilities}
          </h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            {t.capabilitiesDescription}
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div 
                key={feature.title} 
                className="group p-7 rounded-lg border border-border/30 hover:border-border/60 bg-card hover:shadow-lg transition-all duration-200"
              >
                <div className="space-y-4">
                  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors duration-200">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold text-foreground">{feature.title}</h3>
                  <p className="text-base text-muted-foreground leading-relaxed">{feature.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
export default Features;