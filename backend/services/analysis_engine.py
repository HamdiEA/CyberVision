"""
Moteur d'analyse principal.
Orchestre tous les modules forensiques sur une image.
"""

from typing import Dict, Any, cast
import asyncio
from .exif_analysis import analyze_exif
from .structure_analysis import analyze_structure
from .stego_analysis import analyze_steganography
from .ai_analysis import analyze_with_ai
from .risk_calculator import calculate_integrity_score


async def analyze_image(image_data: bytes, filename: str) -> Dict[str, Any]:
    """
    Effectuer l'analyse forensique complète d'une image
    
    Cette fonction orchestre tous les modules d'analyse:
    - Analyse des métadonnées EXIF
    - Analyse structurelle
    - Analyse stéganographique
    - Analyse visuelle par IA
    
    Args:
        image_data: Données binaires de l'image
        filename: Nom du fichier
        
    Returns:
        Dictionnaire contenant tous les résultats d'analyse
    """
    
    # Initialiser les résultats
    results = {
        "filename": filename,
        "status": "processing",
        "error": None,
        "exif_analysis": {},
        "structure_analysis": {},
        "stego_analysis": {},
        "ai_analysis": {},
        "integrity_score": {},
        "timestamp": None
    }
    
    try:
        # Exécuter les analyses en parallèle pour optimiser le temps
        exif_task = asyncio.create_task(run_exif_analysis(image_data))
        structure_task = asyncio.create_task(run_structure_analysis(image_data))
        stego_task = asyncio.create_task(run_stego_analysis(image_data))
        ai_task = asyncio.create_task(run_ai_analysis(image_data))
        
        # Attendre que toutes les analyses soient terminées
        exif_results, structure_results, stego_results, ai_results = await asyncio.gather(
            exif_task,
            structure_task,
            stego_task,
            ai_task,
            return_exceptions=True
        )
        
        # Gérer les exceptions individuelles
        if isinstance(exif_results, Exception):
            exif_results = {"error": str(exif_results), "risk_score": 50}
        if isinstance(structure_results, Exception):
            structure_results = {"error": str(structure_results), "risk_score": 50}
        if isinstance(stego_results, Exception):
            stego_results = {"error": str(stego_results), "risk_score": 0}
        if isinstance(ai_results, Exception):
            ai_results = {"error": str(ai_results), "risk_score": 50}
        
        exif_results = cast(Dict[str, Any], exif_results)
        structure_results = cast(Dict[str, Any], structure_results)
        stego_results = cast(Dict[str, Any], stego_results)
        ai_results = cast(Dict[str, Any], ai_results)

        # Stocker les résultats
        results["exif_analysis"] = exif_results
        results["structure_analysis"] = structure_results
        results["stego_analysis"] = stego_results
        results["ai_analysis"] = ai_results
        
        # Calculer le score d'intégrité global
        results["integrity_score"] = calculate_integrity_score(
            exif_results,
            structure_results,
            stego_results,
            ai_results
        )
        
        # Ajouter le timestamp
        from datetime import datetime
        results["timestamp"] = datetime.now().isoformat()
        
        # Marquer comme terminé
        results["status"] = "completed"
        
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


async def run_exif_analysis(image_data: bytes) -> Dict[str, Any]:
    """
    Exécuter l'analyse EXIF
    
    Args:
        image_data: Données binaires de l'image
        
    Returns:
        Résultats de l'analyse EXIF
    """
    # Exécuter de manière synchrone (les fonctions PIL sont synchrones)
    return analyze_exif(image_data)


async def run_structure_analysis(image_data: bytes) -> Dict[str, Any]:
    """
    Exécuter l'analyse structurelle
    
    Args:
        image_data: Données binaires de l'image
        
    Returns:
        Résultats de l'analyse structurelle
    """
    # Exécuter de manière synchrone
    return analyze_structure(image_data)


async def run_stego_analysis(image_data: bytes) -> Dict[str, Any]:
    """
    Exécuter l'analyse stéganographique
    
    Args:
        image_data: Données binaires de l'image
        
    Returns:
        Résultats de l'analyse stéganographique
    """
    # Exécuter de manière synchrone
    return analyze_steganography(image_data)


async def run_ai_analysis(image_data: bytes) -> Dict[str, Any]:
    """
    Exécuter l'analyse visuelle par IA
    
    Args:
        image_data: Données binaires de l'image
        
    Returns:
        Résultats de l'analyse IA
    """
    # Exécuter de manière asynchrone (appel API externe)
    return await analyze_with_ai(image_data)


def format_results_for_frontend(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formater les résultats pour le frontend
    
    Args:
        results: Résultats bruts de l'analyse
        
    Returns:
        Résultats formatés pour le frontend
    """
    formatted = {
        "success": results.get("status") == "completed",
        "error": results.get("error"),
        "filename": results.get("filename"),
        "timestamp": results.get("timestamp"),
        "integrity": {
            "score": results.get("integrity_score", {}).get("score", 0),
            "risk_level": results.get("integrity_score", {}).get("risk_level", "unknown"),
            # Convertir la confiance de 0-1 en pourcentage pour l'interface.
            "confidence": int(round(results.get("integrity_score", {}).get("confidence", 0) * 100)),
            "summary": results.get("integrity_score", {}).get("summary", ""),
            "recommendations": results.get("integrity_score", {}).get("recommendations", [])
        },
        "modules": {
            "exif": {
                "has_exif": results.get("exif_analysis", {}).get("has_exif", False),
                "camera_info": results.get("exif_analysis", {}).get("camera_info", {}),
                "date_info": results.get("exif_analysis", {}).get("date_info", {}),
                "anomalies": results.get("exif_analysis", {}).get("anomalies", []),
                "risk_score": results.get("exif_analysis", {}).get("risk_score", 0)
            },
            "structure": {
                "file_format": results.get("structure_analysis", {}).get("file_format", ""),
                "dimensions": results.get("structure_analysis", {}).get("dimensions"),
                "color_mode": results.get("structure_analysis", {}).get("color_mode", ""),
                "is_corrupted": results.get("structure_analysis", {}).get("is_corrupted", False),
                "entropy": results.get("structure_analysis", {}).get("entropy", 0),
                "anomalies": results.get("structure_analysis", {}).get("anomalies", []),
                "risk_score": results.get("structure_analysis", {}).get("risk_score", 0)
            },
            "steganography": {
                "suspicious": results.get("stego_analysis", {}).get("suspicious", False),
                "confidence": results.get("stego_analysis", {}).get("confidence", 0),
                "anomalies": results.get("stego_analysis", {}).get("anomalies", []),
                "risk_score": results.get("stego_analysis", {}).get("risk_score", 0)
            },
            "ai_visual": {
                "authenticity": results.get("ai_analysis", {}).get("authenticity", "unknown"),
                "retouches_detected": results.get("ai_analysis", {}).get("retouches_detected", False),
                "retouches_details": results.get("ai_analysis", {}).get("retouches_details", ""),
                "visual_inconsistencies": results.get("ai_analysis", {}).get("visual_inconsistencies", []),
                "confidence_score": results.get("ai_analysis", {}).get("confidence_score", 50),
                "explanation": results.get("ai_analysis", {}).get("explanation", ""),
                "risk_score": results.get("ai_analysis", {}).get("risk_score", 50)
            }
        }
    }
    
    return formatted