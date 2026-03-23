// Barre de navigation principale avec bascule de theme.
import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/hooks/useTheme";
import { useLanguage, translations } from "@/hooks/useLanguage";
import { Link } from "react-router-dom";

// Affiche l'en-tete global et les liens de navigation.
export default function Header() {
  const { theme, setTheme } = useTheme();
  const { language } = useLanguage();
  const t = translations[language];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/30 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto relative flex h-20 items-center px-4">
        <Link to="/" className="-ml-1 md:-ml-3 flex items-center gap-4 hover:opacity-80 transition-opacity">
          <img
            src="/LOGO.png"
            alt="Logo CyberVision"
            className="h-14 w-14 scale-[2] object-contain origin-center"
          />
          <div className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent tracking-tight">
            CyberVision
          </div>
        </Link>

        <nav className="hidden md:flex absolute left-1/2 -translate-x-1/2 items-center gap-8">
          <Link to="/" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-200">
            {t.home}
          </Link>
          <Link to="/how-to-use" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-200">
            {t.howToUse}
          </Link>
          <Link to="/upload" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-200">
            {t.analyze}
          </Link>
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            className="inline-flex items-center justify-center rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors duration-200"
            title={theme === "light" ? "Passer en mode sombre" : "Passer en mode clair"}
          >
            {theme === "light" ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
