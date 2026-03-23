"""
Service d'analyse structurelle.
Contrôle la cohérence interne des fichiers image.
"""

from typing import Dict, Any, List
import numpy as np
from PIL import Image
import io
import hashlib


def analyze_structure(image_data: bytes) -> Dict[str, Any]:
    """
    Analyser la structure interne d'une image
    
    Args:
        image_data: Données binaires de l'image
        
    Returns:
        Dictionnaire contenant les résultats de l'analyse structurelle
    """
    
    results = {
        "file_format": None,
        "file_size": len(image_data),
        "dimensions": None,
        "color_mode": None,
        "is_corrupted": False,
        "magic_numbers": {},
        "entropy": 0,
        "anomalies": [],
        "risk_score": 0
    }
    
    try:
        # Ouvrir l'image avec PIL
        image = Image.open(io.BytesIO(image_data))
        
        # Extraire les informations de base
        results["file_format"] = image.format
        results["dimensions"] = image.size
        results["color_mode"] = image.mode
        
        # Vérifier les magic numbers
        detected_format = image.format or "UNKNOWN"
        results["magic_numbers"] = check_magic_numbers(image_data, detected_format)
        
        # Calculer l'entropie
        results["entropy"] = calculate_entropy(image_data)
        
        # Détecter les anomalies structurelles
        results["anomalies"] = detect_structure_anomalies(
            image_data, image, results["magic_numbers"], results["entropy"]
        )
        
        # Vérifier la corruption
        results["is_corrupted"] = check_corruption(image_data, image)
        
        # Calculer le score de risque
        results["risk_score"] = calculate_structure_risk_score(
            results["is_corrupted"],
            results["anomalies"],
            results["magic_numbers"],
            results["entropy"]
        )
        
    except Exception as e:
        results["is_corrupted"] = True
        results["anomalies"].append(f"Erreur lors de l'analyse structurelle: {str(e)}")
        results["risk_score"] = 80
    
    return results


def check_magic_numbers(image_data: bytes, image_format: str) -> Dict[str, Any]:
    """
    Vérifier les magic numbers du fichier
    
    Args:
        image_data: Données binaires de l'image
        image_format: Format de l'image détecté par PIL
        
    Returns:
        Dictionnaire avec les résultats de vérification
    """
    magic_info = {
        "expected": None,
        "actual": None,
        "valid": True,
        "details": None
    }
    
    # Magic numbers par format
    magic_numbers = {
        "JPEG": [b'\xff\xd8\xff'],
        "PNG": [b'\x89PNG\r\n\x1a\n'],
        "BMP": [b'BM']
    }
    
    if image_format in magic_numbers:
        expected_signatures = magic_numbers[image_format]
        magic_info["expected"] = [sig.hex() for sig in expected_signatures]
        
        # Obtenir les premiers bytes
        header = image_data[:8]
        magic_info["actual"] = header.hex()
        
        # Vérifier si le header correspond
        valid = False
        for signature in expected_signatures:
            if header.startswith(signature):
                valid = True
                magic_info["details"] = f"Magic numbers valides pour {image_format}"
                break
        
        if not valid:
            magic_info["valid"] = False
            magic_info["details"] = f"Magic numbers invalides pour {image_format}"
    else:
        magic_info["details"] = f"Format {image_format} non vérifié pour les magic numbers"
    
    return magic_info


def calculate_entropy(image_data: bytes) -> float:
    """
    Calculer l'entropie des données de l'image
    
    L'entropie mesure le caractère aléatoire des données.
    Une entropie élevée peut indiquer:
    - Données compressées
    - Stéganographie
    - Cryptage
    
    Args:
        image_data: Données binaires de l'image
        
    Returns:
        Valeur d'entropie (0-8)
    """
    # Compter la fréquence de chaque byte
    byte_counts = np.zeros(256, dtype=np.float64)
    
    for byte in image_data:
        byte_counts[byte] += 1
    
    # Calculer les probabilités
    probabilities = byte_counts / len(image_data)
    
    # Filtrer les probabilités non nulles
    probabilities = probabilities[probabilities > 0]
    
    # Calculer l'entropie en bits
    entropy = -np.sum(probabilities * np.log2(probabilities))
    
    return float(entropy)


def detect_structure_anomalies(
    image_data: bytes,
    image: Image.Image,
    magic_numbers: Dict[str, Any],
    entropy: float
) -> List[str]:
    """
    Détecter les anomalies structurelles
    
    Args:
        image_data: Données binaires de l'image
        image: Objet Image PIL
        magic_numbers: Résultats de vérification des magic numbers
        entropy: Valeur d'entropie
        
    Returns:
        Liste des anomalies détectées
    """
    anomalies = []
    
    # Vérifier les magic numbers
    if not magic_numbers.get("valid", True):
        anomalies.append(magic_numbers.get("details", "Magic numbers invalides"))
    
    # Vérifier l'entropie (valeurs suspectes)
    if entropy > 7.8:
        anomalies.append(f"Entropie très élevée ({entropy:.2f}) - possible stéganographie ou cryptage")
    elif entropy < 7.0 and entropy > 4.0:
        anomalies.append(f"Entropie anormalement basse ({entropy:.2f}) - possible manipulation")
    
    # Vérifier la taille du fichier
    file_size = len(image_data)
    width, height = image.size
    pixels = width * height
    
    # Estimation grossière de la taille attendue
    expected_size = pixels * 3  # 3 bytes par pixel pour RGB
    compression_ratio = file_size / expected_size if expected_size > 0 else 0
    
    if compression_ratio < 0.1:
        anomalies.append("Taux de compression anormalement bas")
    elif compression_ratio > 2.0:
        anomalies.append("Taille de fichier anormalement élevée pour les dimensions")
    
    # Vérifier les dimensions suspectes
    if width == 0 or height == 0:
        anomalies.append("Dimensions invalides")
    elif width < 32 or height < 32:
        anomalies.append("Dimensions très petites - possible thumbnail")
    
    return anomalies


def check_corruption(image_data: bytes, image: Image.Image) -> bool:
    """
    Vérifier si le fichier est corrompu
    
    Args:
        image_data: Données binaires de l'image
        image: Objet Image PIL
        
    Returns:
        True si le fichier est corrompu, False sinon
    """
    try:
        # Essayer de charger l'image
        image.load()
        
        # Vérifier que les données sont cohérentes
        width, height = image.size
        if width <= 0 or height <= 0:
            return True
        
        # Essayer d'accéder aux pixels
        try:
            image.getpixel((0, 0))
        except:
            return True
        
        return False
        
    except Exception:
        return True


def calculate_structure_risk_score(
    is_corrupted: bool,
    anomalies: List[str],
    magic_numbers: Dict[str, Any],
    entropy: float
) -> int:
    """
    Calculer un score de risque basé sur l'analyse structurelle
    
    Args:
        is_corrupted: Si le fichier est corrompu
        anomalies: Liste des anomalies
        magic_numbers: Résultats de vérification des magic numbers
        entropy: Valeur d'entropie
        
    Returns:
        Score de risque (0-100, plus élevé = plus risqué)
    """
    risk_score = 0
    
    # Fichier corrompu = risque élevé
    if is_corrupted:
        risk_score += 80
    
    # Magic numbers invalides
    if not magic_numbers.get("valid", True):
        risk_score += 40
    
    # Risque basé sur les anomalies
    risk_score += len(anomalies) * 15
    
    # Risque basé sur l'entropie
    if entropy > 7.8:
        risk_score += 30  # Possible stéganographie
    elif entropy < 4.0:
        risk_score += 20  # Très bas entropie
    
    # Limiter le score à 100
    return min(risk_score, 100)