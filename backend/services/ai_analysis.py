"""
Service d'analyse visuelle locale.
Évalue l'image avec des heuristiques sans appel IA externe.
"""

from typing import Dict, Any
from PIL import Image, ImageStat
import io
import numpy as np

try:
    import cv2  
except Exception: 
    cv2 = None


async def analyze_with_ai(image_data: bytes) -> Dict[str, Any]:
    # Lance l'analyse visuelle locale et renvoie un résultat standardisé.
    """
    Analyse visuelle heuristique (sans service externe).

    Args:
        image_data: Données binaires de l'image

    Returns:
        Dictionnaire contenant les résultats de l'analyse visuelle
    """

    try:
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        metrics = _basic_visual_metrics(image)
        cv2_metrics = _cv2_visual_metrics(image)
        cv2_notes = cv2_metrics.pop("notes", []) if isinstance(cv2_metrics, dict) else []
        metrics["notes"].extend(cv2_notes)
        metrics.update(cv2_metrics)
        risk_score = _estimate_risk(metrics)
        confidence = max(0, min(100, 100 - risk_score))

        return {
            "model_used": "local-heuristic",
            "authenticity": "unknown",
            "retouches_detected": False,
            "retouches_details": "Aucune retouche évidente détectée par les heuristiques locales.",
            "visual_inconsistencies": metrics["notes"],
            "confidence_score": int(confidence),
            "explanation": metrics["summary"],
            "full_analysis": metrics,
            "suspicious_areas": [],
            "risk_score": int(risk_score),
        }

    except Exception as e:
        print(f"[ERROR] Erreur lors de l'analyse visuelle: {str(e)}")
        return get_fallback_analysis(error=str(e))


def _basic_visual_metrics(image: Image.Image) -> Dict[str, Any]:
    # Calcule des métriques simples: taille, luminosité et contraste.
    stats = ImageStat.Stat(image)
    width, height = image.size

    # luminance approximative en utilisant la moyenne des canaux
    mean_rgb = stats.mean
    mean_brightness = sum(mean_rgb) / 3

    # estimation simple du contraste via l'écart-type moyen des canaux
    stddev_rgb = stats.stddev
    contrast = sum(stddev_rgb) / 3

    notes = []
    if width < 256 or height < 256:
        notes.append("Faible résolution: certaines analyses peuvent être limitées.")
    if contrast < 5:
        notes.append("Contraste très faible: possible image floue ou compressée.")
    if mean_brightness < 20:
        notes.append("Image très sombre: indices visuels limités.")
    if mean_brightness > 235:
        notes.append("Image très claire: risque de zones brûlées.")

    summary = (
        f"Dimensions {width}x{height}, luminosité moyenne {mean_brightness:.1f}, "
        f"contraste {contrast:.1f}."
    )

    return {
        "width": width,
        "height": height,
        "mean_brightness": mean_brightness,
        "contrast": contrast,
        "notes": notes,
        "summary": summary,
    }


def _cv2_visual_metrics(image: Image.Image) -> Dict[str, Any]:
    # Mesure des signaux visuels OpenCV: arêtes, netteté et bruit.
    """
    Heuristiques OpenCV: densité d'arêtes, niveau de flou et bruit.
    """
    if cv2 is None:
        return {
            "edge_density": None,
            "laplacian_var": None,
            "noise_sigma": None,
        }

    arr = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    # Variance du Laplacien: faible -> flou/softening, élevé -> sur-accentuation
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # Densité d'arêtes via Canny
    edges = cv2.Canny(gray, 100, 200)
    edge_density = float(np.mean(edges > 0))

    # Bruit estimé par l'écart-type du canal gris
    noise_sigma = float(np.std(gray))

    notes = []
    if lap_var < 20:
        notes.append("Faible netteté détectée (Laplacien bas)")
    if lap_var > 250:
        notes.append("Accentuation très forte des contours")
    if edge_density < 0.01:
        notes.append("Très peu d'arêtes détectées")
    if edge_density > 0.2:
        notes.append("Densité d'arêtes élevée, possible surcontraste ou retouche")
    if noise_sigma > 70:
        notes.append("Niveau de bruit élevé")

    return {
        "edge_density": edge_density,
        "laplacian_var": lap_var,
        "noise_sigma": noise_sigma,
        "notes": notes,
    }


def _estimate_risk(metrics: Dict[str, Any]) -> float:
    # Convertit les métriques visuelles en score de risque global.
    risk = 20.0  # base uncertainty without external AI

    if metrics["mean_brightness"] < 20 or metrics["mean_brightness"] > 235:
        risk += 10
    if metrics["contrast"] < 5:
        risk += 15
    if metrics["width"] < 256 or metrics["height"] < 256:
        risk += 10

    lap = metrics.get("laplacian_var")
    if isinstance(lap, (int, float)):
        if lap < 20:
            risk += 10  # blur/softening
        if lap > 250:
            risk += 8   # over-sharpening

    edge_density = metrics.get("edge_density")
    if isinstance(edge_density, (int, float)):
        if edge_density < 0.01 or edge_density > 0.25:
            risk += 5

    noise_sigma = metrics.get("noise_sigma")
    if isinstance(noise_sigma, (int, float)) and noise_sigma > 70:
        risk += 10

    risk = min(100.0, max(0.0, risk))
    return risk

def get_fallback_analysis(error: str | None = None) -> Dict[str, Any]:
    # Fournit une réponse de secours si l'analyse locale échoue.
    return {
        "model_used": "local-heuristic",
        "authenticity": "unknown",
        "retouches_detected": False,
        "retouches_details": "",
        "visual_inconsistencies": [],
        "confidence_score": 50,
        "explanation": error or "Analyse visuelle limitée aux heuristiques locales.",
        "full_analysis": {},
        "suspicious_areas": [],
        "risk_score": 50,
    }
