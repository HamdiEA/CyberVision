// Gestion du theme clair/sombre pour toute l'application.
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

type Theme = "light" | "dark";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Fournit l'etat de theme et la fonction de mise a jour.
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      const stored = localStorage.getItem("theme") as Theme | null;
      if (stored) return stored;
      return "light"; // Mode clair par défaut.
    } catch {
      return "light"; // Mode clair par défaut en cas d'erreur.
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem("theme", theme);
    } catch (e) {
      console.error("Erreur lors de l'enregistrement du thème:", e);
    }
    const html = document.documentElement;
    if (theme === "dark") {
      html.classList.add("dark");
    } else {
      html.classList.remove("dark");
    }
  }, [theme]);

  const handleSetTheme = (newTheme: Theme) => {
    setTheme(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme: handleSetTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  // Expose le contexte theme avec garde de securite.
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme doit être utilisé à l'intérieur de ThemeProvider");
  }
  return context;
}
