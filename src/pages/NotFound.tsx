// Page 404 simple pour les routes inconnues.
import { useLocation } from "react-router-dom";
import { useEffect } from "react";

// Affiche un message de page introuvable.
const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 - route inconnue", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background text-center">
      <div className="space-y-3">
        <h1 className="text-5xl font-bold">404</h1>
        <p className="text-lg text-muted-foreground">Page non trouvée</p>
        <a href="/" className="btn-primary inline-flex">Retour à l'accueil</a>
      </div>
    </div>
  );
};

export default NotFound;
