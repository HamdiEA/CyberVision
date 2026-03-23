// Gestion de la langue interface et dictionnaire de traductions.
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

type Language = "fr";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Fournit la langue active et la fonction de changement de langue.
export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>("fr");

  useEffect(() => {
    try {
      localStorage.setItem("language", language);
    } catch (e) {
      console.error("Erreur lors de l'enregistrement de la langue:", e);
    }
  }, [language]);

  const setLanguage = (_lang: Language) => {
    setLanguageState("fr");
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  // Expose le contexte langue avec verification d'usage.
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage doit être utilisé à l'intérieur de LanguageProvider");
  }
  return context;
}

// Table des textes traduits utilises dans l'interface.
export const translations = {
  en: {
    home: "Home",
    analyze: "Analyze",
    howToUse: "How To Use",
    results: "Results",
    gallery: "Gallery",
    features: "Features",
    documentation: "Documentation",
    startAnalysis: "Start Analysis",
    forensicAnalysis: "Digital Forensics & Image Analysis",
    platformDescription: "Advanced AI-powered digital forensics and image analysis platform",
    analyzeImage: "Analyze Image",
    viewDocumentation: "View Documentation",
    imagesAnalyzed: "Images Analyzed",
    anomaliesDetected: "Anomalies Detected",
    accuracyRate: "Accuracy Rate",
    analysisTypes: "Analysis Types",
    coreCapabilities: "Core Capabilities",
    capabilitiesDescription:
      "AI detects tampering, identifies suspicious patterns, analyzes metadata, and highlights forensic anomalies in your digital evidence.",
    howItWorks: "How It Works",
    uploadDescription:
      "Upload your image, our AI applies advanced forensic algorithms to detect anomalies and tampering, then highlights suspicious areas and metadata inconsistencies. All analysis happens in your browser.",
    preprocessing: "Image Preprocessing",
    preprocessingDesc: "Normalization and enhancement to reveal tampering artifacts and hidden information.",
    detection: "Forensic Detection",
    detectionDesc: "Advanced AI detects ELA anomalies, steganography, tampering patterns, and metadata inconsistencies.",
    reporting: "Report Generation",
    reportingDesc: "Detailed forensic report with confidence scores, evidence mapping, and actionable recommendations.",
    analyzeEvidence: "Analyze Digital Evidence",
    advancedAiDetection: "Advanced AI Detection",
    advancedAiDesc:
      "Deep learning algorithms trained on thousands of forensic images for precise anomaly detection and classification.",
    realtimeAnalysis: "Real-time Analysis",
    realtimeDesc: "Process images instantly with detailed forensic results in seconds using optimized inference.",
    multiLayerSecurity: "Multi-Layer Security",
    multiLayerSecurityDesc: "Detect tampering, steganography, metadata anomalies, and file structure inconsistencies simultaneously.",
    comprehensiveReporting: "Comprehensive Reporting",
    comprehensiveReportingDesc: "Generate detailed forensic reports with evidence trails, confidence scores, and actionable insights.",
    uploadEvidence: "Drop your digital evidence here",
    selectImages: "Select Image",
    uploadPlaceholder: "Or click to select one image",
    selectedImages: "Selected Image",
    clearAll: "Clear All",
    removeImage: "Remove",
    startForensicAnalysis: "Start Forensic Analysis",
    advancedAnalysis: "Advanced Analysis (Server)",
    analysisResults: "Analysis Results",
    advancedResults: "Advanced Results",
    forensicEvidenceGallery: "Forensic Evidence Gallery",
    searchEvidence: "Search evidence (tampering, metadata, steganography)",
    samples: "Samples",
    evidence: "Evidence",
    archive: "Archive",
    search: "Search",
    searching: "Searching…",
    noResults: "No results. Try a different keyword.",
    forensicFindings: "Forensic Findings",
    clickAnomaly: "Click on an anomaly to view detailed evidence analysis.",
    anomaly: "Anomaly",
    confidence: "Confidence",
    region: "Region",
    size: "Size",
    forensicResults: "Forensic Analysis Results",
    digitalEvidenceAnomalies: "Digital evidence anomalies and tampering indicators",
    tamperingDetected: "Tampering Detected",
    metadataAnomalies: "Metadata Anomalies",
    steganographyRisk: "Steganography Risk",
    fileIntegrity: "File Integrity",
  },
  fr: {
    home: "Accueil",
    analyze: "Analyser",
    howToUse: "Comment utiliser",
    results: "Résultats",
    gallery: "Galerie",
    features: "Fonctionnalités",
    documentation: "Documentation",
    startAnalysis: "Commencer l'analyse",
    forensicAnalysis: "Analyse Forensique & Analyse d'Images",
    platformDescription: "Plateforme d'analyse forensique avancée alimentée par l'IA",
    analyzeImage: "Commencer l'analyse",
    viewDocumentation: "Voir la documentation",
    imagesAnalyzed: "Images analysées",
    anomaliesDetected: "Anomalies détectées",
    accuracyRate: "Taux de précision",
    analysisTypes: "Types d'analyse",
    coreCapabilities: "Fonctionnalités principales",
    capabilitiesDescription:
      "L'IA détecte les manipulations, identifie les motifs suspects, analyse les métadonnées et met en évidence les anomalies forensiques dans vos preuves numériques.",
    howItWorks: "Comment ça marche",
    uploadDescription:
      "Téléchargez votre image, notre IA applique des algorithmes forensiques avancés pour détecter les anomalies et les manipulations, puis met en évidence les zones suspectes et les incohérences de métadonnées. Toute l'analyse se fait dans votre navigateur.",
    preprocessing: "Prétraitement d'image",
    preprocessingDesc: "Normalisation et amélioration pour révéler les artefacts de manipulation et les informations cachées.",
    detection: "Détection forensique",
    detectionDesc: "L'IA avancée détecte les anomalies ELA, la stéganographie, les motifs de manipulation et les incohérences de métadonnées.",
    reporting: "Génération de rapport",
    reportingDesc: "Rapport forensique détaillé avec scores de confiance, cartographie des preuves et recommandations actionnables.",
    analyzeEvidence: "Analyser les preuves numériques",
    advancedAiDetection: "Détection IA avancée",
    advancedAiDesc:
      "Algorithmes de deep learning entraînés sur des milliers d'images forensiques pour une détection précise des anomalies.",
    realtimeAnalysis: "Analyse en temps réel",
    realtimeDesc: "Traitement d'images instantané avec des résultats forensiques détaillés en quelques secondes.",
    multiLayerSecurity: "Sécurité multi-couches",
    multiLayerSecurityDesc: "Détectez les manipulations, la stéganographie, les anomalies de métadonnées et les incohérences de structure de fichier.",
    comprehensiveReporting: "Rapports complets",
    comprehensiveReportingDesc: "Générez des rapports forensiques détaillés avec piste d'audit, scores de confiance et recommandations actionnables.",
    uploadEvidence: "Déposez vos preuves numériques ici",
    selectImages: "Sélectionner une image",
    uploadPlaceholder: "Ou cliquez pour sélectionner une image",
    selectedImages: "Image sélectionnée",
    clearAll: "Effacer tout",
    removeImage: "Supprimer",
    startForensicAnalysis: "Commencer l'analyse forensique",
    advancedAnalysis: "Analyse avancée (Serveur)",
    analysisResults: "Résultats de l'analyse",
    advancedResults: "Résultats avancés",
    forensicEvidenceGallery: "Galerie de preuves forensiques",
    searchEvidence: "Rechercher des preuves (manipulation, métadonnées, stéganographie)",
    samples: "Échantillons",
    evidence: "Preuves",
    archive: "Archive",
    search: "Rechercher",
    searching: "Recherche…",
    noResults: "Aucun résultat. Essayez un mot-clé différent.",
    forensicFindings: "Résultats Forensiques",
    clickAnomaly: "Cliquez sur une anomalie pour afficher l'analyse détaillée des preuves.",
    anomaly: "Anomalie",
    confidence: "Confiance",
    region: "Région",
    size: "Taille",
    forensicResults: "Résultats de l'analyse forensique",
    digitalEvidenceAnomalies: "Anomalies des preuves numériques et indicateurs de manipulation",
    tamperingDetected: "Manipulation détectée",
    metadataAnomalies: "Anomalies de métadonnées",
    steganographyRisk: "Risque de stéganographie",
    fileIntegrity: "Intégrité des fichiers",
  },
};
