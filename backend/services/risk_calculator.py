"""
Service de calcul du risque.
Produit le score d'intégrité global et le niveau de risque.
"""

from typing import Dict, Any, List

def calculate_integrity_score(
    exif_results: Dict[str, Any],
    structure_results: Dict[str, Any],
    stego_results: Dict[str, Any],
    ai_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculer le score d'intégrité global de l'image
    
    Agrège les résultats de tous les modules d'analyse et produit :
    - Un score d'intégrité de 0 à 100 (100 = authentique, 0 = fortement manipulé)
    - Un niveau de risque (faible, moyen, élevé, critique)
    - Un résumé compréhensible
    - Des recommandations
    
    Args:
        exif_results: Résultats de l'analyse EXIF
        structure_results: Résultats de l'analyse structurelle
        stego_results: Résultats de l'analyse stéganographique
        ai_results: Résultats de l'analyse IA
    
    Returns:
        Dictionnaire avec le score d'intégrité et les métadonnées
    """
    
    # Extraire les scores de risque de chaque module
    exif_risk = exif_results.get("risk_score", 0)
    structure_risk = structure_results.get("risk_score", 0)
    stego_risk = stego_results.get("risk_score", 0)
    ai_risk = ai_results.get("risk_score", 0)
    
    # Pondération des différents modules
    # L'analyse IA a le poids le plus important
    weights = {
        "exif": 0.20,
        "structure": 0.20,
        "stego": 0.25,
        "ai": 0.35
    }
    
    # Calculer le score de risque pondéré
    weighted_risk_score = (
        exif_risk * weights["exif"] +
        structure_risk * weights["structure"] +
        stego_risk * weights["stego"] +
        ai_risk * weights["ai"]
    )
    
    # Convertir le score de risque en score d'intégrité (inversé)
    # Risque élevé = intégrité basse
    integrity_score = int(100 - weighted_risk_score)
    
    # Déterminer le niveau de risque
    risk_level = determine_risk_level(integrity_score)
    
    # Calculer la confiance de l'analyse
    confidence = calculate_confidence(
        exif_results,
        structure_results,
        stego_results,
        ai_results
    )
    
    # Générer le résumé
    summary = generate_summary(
        integrity_score,
        risk_level,
        exif_results,
        structure_results,
        stego_results,
        ai_results
    )
    
    # Générer les recommandations
    recommendations = generate_recommendations(
        integrity_score,
        risk_level,
        exif_results,
        structure_results,
        stego_results,
        ai_results
    )
    
    # Compter les anomalies totales
    total_anomalies = count_total_anomalies(
        exif_results,
        structure_results,
        stego_results,
        ai_results
    )
    
    return {
        "score": integrity_score,
        "risk_level": risk_level,
        "confidence": confidence,
        "summary": summary,
        "recommendations": recommendations,
        "total_anomalies": total_anomalies,
        "module_scores": {
            "exif": {
                "risk": exif_risk,
                "integrity": 100 - exif_risk,
                "weight": weights["exif"]
            },
            "structure": {
                "risk": structure_risk,
                "integrity": 100 - structure_risk,
                "weight": weights["structure"]
            },
            "steganography": {
                "risk": stego_risk,
                "integrity": 100 - stego_risk,
                "weight": weights["stego"]
            },
            "ai_visual": {
                "risk": ai_risk,
                "integrity": 100 - ai_risk,
                "weight": weights["ai"]
            }
        }
    }

def determine_risk_level(integrity_score: int) -> str:
    """
    Déterminer le niveau de risque basé sur le score d'intégrité
    
    Args:
        integrity_score: Score de 0 à 100
    
    Returns:
        Niveau de risque: "faible", "moyen", "élevé", "critique"
    """
    if integrity_score >= 85:
        return "faible"  # Authentique / Faible risque
    elif integrity_score >= 70:
        return "moyen"  # Attention / Risque moyen
    elif integrity_score >= 40:
        return "élevé"  # Suspect / Risque élevé
    else:
        return "critique"  # Très haut risque

def calculate_confidence(
    exif_results: Dict,
    structure_results: Dict,
    stego_results: Dict,
    ai_results: Dict
) -> float:
    """
    Calculer le niveau de confiance de l'analyse
    
    Returns:
        Score de confiance de 0 à 1
    """
    confidence_factors = []
    
    # Confiance EXIF
    if exif_results.get("has_exif", False):
        confidence_factors.append(0.9)
    else:
        confidence_factors.append(0.5)
    
    # Confiance structure
    if not structure_results.get("is_corrupted", True):
        confidence_factors.append(0.95)
    else:
        confidence_factors.append(0.3)
    
    # Confiance IA
    ai_confidence = ai_results.get("confidence_score", 50) / 100
    confidence_factors.append(ai_confidence)
    
    # Moyenne
    avg_confidence = sum(confidence_factors) / len(confidence_factors)
    
    return round(avg_confidence, 2)

def generate_summary(
    integrity_score: int,
    risk_level: str,
    exif_results: Dict,
    structure_results: Dict,
    stego_results: Dict,
    ai_results: Dict
) -> str:
    """
    Générer un résumé compréhensible de l'analyse
    
    Returns:
        Chaîne de résumé pédagogique
    """
    summaries = []
    
    # Résumé basé sur le score
    if integrity_score >= 85:
        summaries.append("L'image semble authentique (risque faible).")
    elif integrity_score >= 70:
        summaries.append("L'image présente quelques anomalies mineures (risque moyen).")
    elif integrity_score >= 40:
        summaries.append("L'image est probablement modifiée ou manipulée (risque élevé).")
    else:
        summaries.append("L'image est fortement suspecte et probablement falsifiée (risque critique).")
    
    # Détails EXIF
    if not exif_results.get("has_exif", True):
        summaries.append("Les métadonnées EXIF sont absentes ou ont été supprimées.")
    elif exif_results.get("anomalies"):
        summaries.append(f"Anomalies EXIF détectées: {', '.join(exif_results['anomalies'][:2])}")
    
    # Détails IA
    ai_authenticity = ai_results.get("authenticity", "unknown")
    if ai_authenticity == "manipulated":
        summaries.append("L'analyse IA a détecté des manipulations visuelles.")
    elif ai_authenticity == "suspect":
        summaries.append("L'analyse IA suggère des modifications possibles.")
    
    # Stéganographie
    if stego_results.get("suspicious", False):
        summaries.append("Indices de stéganographie ou données cachées détectées.")
    
    return " ".join(summaries)

def generate_recommendations(
    integrity_score: int,
    risk_level: str,
    exif_results: Dict,
    structure_results: Dict,
    stego_results: Dict,
    ai_results: Dict
) -> List[str]:
    """
    Générer des recommandations basées sur l'analyse
    
    Returns:
        Liste de recommandations
    """
    recommendations = []
    
    # Recommandations basées sur le niveau de risque
    if risk_level == "critical":
        recommendations.append("Ne pas utiliser cette image pour des besoins officiels")
        recommendations.append("Effectuer une analyse forensique approfondie")
        recommendations.append("Vérifier la source et la provenance de l'image")
    elif risk_level == "suspect":
        recommendations.append("Vérification manuelle recommandée")
        recommendations.append("Comparer avec d'autres sources si possible")
        recommendations.append("Utiliser avec précaution")
    elif risk_level == "warning":
        recommendations.append("Vérifier les anomalies détectées")
        recommendations.append("Conserver une trace de l'analyse")
    else:
        recommendations.append("Image utilisable en toute confiance")
        recommendations.append("Aucune action particulière requise")
    
    # Recommandations spécifiques EXIF
    if not exif_results.get("has_exif", True):
        recommendations.append("Rechercher la version originale avec métadonnées")
    
    # Recommandations stéganographie
    if stego_results.get("suspicious", False):
        recommendations.append("Analyser avec des outils spécialisés de stéganographie")
    
    # Recommandations IA
    if ai_results.get("retouches_detected", False):
        recommendations.append("Examiner les zones identifiées comme retouchées")
    
    return recommendations

def count_total_anomalies(
    exif_results: Dict,
    structure_results: Dict,
    stego_results: Dict,
    ai_results: Dict
) -> int:
    """
    Compter le nombre total d'anomalies détectées
    
    Returns:
        Nombre d'anomalies
    """
    count = 0
    
    # Anomalies EXIF
    count += len(exif_results.get("anomalies", []))
    
    # Anomalies structurelles
    count += len(structure_results.get("anomalies", []))
    
    # Stéganographie
    if stego_results.get("suspicious", False):
        count += 1
    
    # Anomalies IA
    if ai_results.get("retouches_detected", False):
        count += 1
    
    count += len(ai_results.get("visual_inconsistencies", []))
    
    return count
