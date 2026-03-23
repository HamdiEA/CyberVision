"""
Service d'analyse EXIF.
Extrait et vérifie les métadonnées des images numériques.
"""

from typing import Dict, Any, List
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import io


def analyze_exif(image_data: bytes) -> Dict[str, Any]:
    """
    Analyser les métadonnées EXIF d'une image
    
    Args:
        image_data: Données binaires de l'image
        
    Returns:
        Dictionnaire contenant les résultats de l'analyse EXIF
    """
    
    results = {
        "has_exif": False,
        "exif_data": {},
        "camera_info": {},
        "date_info": {},
        "location_info": {},
        "anomalies": [],
        "risk_score": 0
    }
    
    try:
        # Ouvrir l'image avec PIL
        image = Image.open(io.BytesIO(image_data))
        
        # Obtenir les données EXIF (Pillow) et tenter un parsing enrichi via piexif
        getexif = getattr(image, "_getexif", None)
        raw_exif = getexif() if callable(getexif) else None
        exif_data = raw_exif if isinstance(raw_exif, dict) else {}
        piexif_data = load_piexif_dict(image_data)
        if piexif_data:
            exif_data = merge_exif_dicts(exif_data, piexif_data)
        
        if exif_data:
            results["has_exif"] = True
            
            # Parser les données EXIF
            parsed_exif = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, str(tag_id)) if isinstance(tag_id, int) else str(tag_id)
                # Convertir les bytes en string si nécessaire
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        value = str(value)
                parsed_exif[tag_name] = value
            
            results["exif_data"] = parsed_exif
            
            # Extraire les informations de caméra
            results["camera_info"] = extract_camera_info(parsed_exif)
            
            # Extraire les informations de date
            results["date_info"] = extract_date_info(parsed_exif)
            
            # Extraire les informations de localisation
            results["location_info"] = extract_location_info(parsed_exif)
            
            # Détecter les anomalies
            results["anomalies"] = detect_exif_anomalies(parsed_exif, image)
            
            # Calculer le score de risque
            results["risk_score"] = calculate_exif_risk_score(
                results["has_exif"],
                results["anomalies"],
                results["camera_info"],
                results["date_info"]
            )
        else:
            # Pas de données EXIF
            results["anomalies"].append("Aucune métadonnée EXIF trouvée - peut être supprimée")
            results["risk_score"] = 20
            
    except Exception as e:
        results["anomalies"].append(f"Erreur lors de l'analyse EXIF: {str(e)}")
        results["risk_score"] = 30
    
    return results


def extract_camera_info(exif_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extraire les informations de caméra depuis les données EXIF
    
    Args:
        exif_data: Données EXIF parsées
        
    Returns:
        Dictionnaire avec les informations de caméra
    """
    camera_info = {}
    
    # Marque de l'appareil
    if "Make" in exif_data:
        camera_info["make"] = exif_data["Make"]
    
    # Modèle de l'appareil
    if "Model" in exif_data:
        camera_info["model"] = exif_data["Model"]
    
    # Logiciel de traitement
    if "Software" in exif_data:
        camera_info["software"] = exif_data["Software"]
    
    # Paramètres d'exposition
    if "ExposureTime" in exif_data:
        camera_info["exposure_time"] = str(exif_data["ExposureTime"])
    
    if "FNumber" in exif_data:
        camera_info["f_number"] = str(exif_data["FNumber"])
    
    if "ISOSpeedRatings" in exif_data:
        camera_info["iso"] = str(exif_data["ISOSpeedRatings"])
    
    if "FocalLength" in exif_data:
        camera_info["focal_length"] = str(exif_data["FocalLength"])
    
    return camera_info


def load_piexif_dict(image_data: bytes) -> Dict[str, Any]:
    """
    Charger les données EXIF avec piexif pour obtenir des tags supplémentaires.
    """
    try:
        exif_dict = piexif.load(image_data)
        parsed: Dict[str, Any] = {}
        for ifd_name in ("0th", "Exif", "GPS", "1st"):
            if ifd_name not in exif_dict:
                continue
            ifd = exif_dict[ifd_name]
            for tag, value in ifd.items():
                tag_info = piexif.TAGS.get(ifd_name, {}).get(tag, {})
                tag_name = tag_info.get("name", tag)
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="ignore")
                    except Exception:
                        value = str(value)
                parsed[tag_name] = value
        return parsed
    except Exception:
        return {}


def merge_exif_dicts(pillow_exif: Dict[str, Any] | None, piexif_exif: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionner les données EXIF Pillow et piexif (piexif prioritaire si présent).
    """
    merged: Dict[str, Any] = {}
    if pillow_exif:
        for tag_id, value in pillow_exif.items():
            tag_name = TAGS.get(tag_id, str(tag_id)) if isinstance(tag_id, int) else str(tag_id)
            merged[tag_name] = value
    if piexif_exif:
        merged.update(piexif_exif)
    return merged


def extract_date_info(exif_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extraire les informations de date depuis les données EXIF
    
    Args:
        exif_data: Données EXIF parsées
        
    Returns:
        Dictionnaire avec les informations de date
    """
    date_info = {}
    
    # Date de prise de vue
    if "DateTimeOriginal" in exif_data:
        date_info["date_taken"] = exif_data["DateTimeOriginal"]
    
    # Date de digitalisation
    if "DateTimeDigitized" in exif_data:
        date_info["date_digitized"] = exif_data["DateTimeDigitized"]
    
    # Date de modification
    if "DateTime" in exif_data:
        date_info["date_modified"] = exif_data["DateTime"]
    
    return date_info


def extract_location_info(exif_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extraire les informations de localisation depuis les données EXIF
    
    Args:
        exif_data: Données EXIF parsées
        
    Returns:
        Dictionnaire avec les informations de localisation
    """
    location_info = {
        "has_gps": False,
        "coordinates": None
    }
    
    # Coordonnées GPS
    if "GPSInfo" in exif_data:
        location_info["has_gps"] = True
        # Note: Parsing GPS complet nécessite plus de traitement
        location_info["gps_data"] = "Données GPS présentes"
    
    return location_info


def detect_exif_anomalies(exif_data: Dict[str, Any], image: Image.Image) -> List[str]:
    """
    Détecter les anomalies dans les métadonnées EXIF
    
    Args:
        exif_data: Données EXIF parsées
        image: Objet Image PIL
        
    Returns:
        Liste des anomalies détectées
    """
    anomalies = []
    
    # Vérifier l'incohérence entre la date de prise de vue et de modification
    if "DateTimeOriginal" in exif_data and "DateTime" in exif_data:
        date_original = exif_data["DateTimeOriginal"]
        date_modified = exif_data["DateTime"]
        if date_original != date_modified:
            anomalies.append("La date de modification diffère de la date de prise de vue")
    
    # Vérifier l'absence de marque de caméra
    if "Make" not in exif_data and "Model" not in exif_data:
        anomalies.append("Aucune information de caméra détectée")
    
    # Vérifier la présence de logiciels d'édition
    if "Software" in exif_data:
        software = exif_data["Software"].lower()
        editing_software = ["photoshop", "gimp", "lightroom", "sketchup", "paint.net"]
        for soft in editing_software:
            if soft in software:
                anomalies.append(f"Logiciel d'édition détecté: {exif_data['Software']}")
                break
    
    # Vérifier l'orientation de l'image
    if "Orientation" in exif_data:
        orientation = exif_data["Orientation"]
        if orientation != 1:
            anomalies.append(f"Orientation de l'image modifiée: {orientation}")
    
    return anomalies


def calculate_exif_risk_score(
    has_exif: bool,
    anomalies: List[str],
    camera_info: Dict[str, Any],
    date_info: Dict[str, Any]
) -> int:
    """
    Calculer un score de risque basé sur l'analyse EXIF
    
    Args:
        has_exif: Présence de données EXIF
        anomalies: Liste des anomalies
        camera_info: Informations de caméra
        date_info: Informations de date
        
    Returns:
        Score de risque (0-100, plus élevé = plus risqué)
    """
    risk_score = 0
    
    # Si pas de données EXIF, risque modéré
    if not has_exif:
        risk_score += 20
    
    # Risque basé sur les anomalies
    risk_score += len(anomalies) * 10
    
    # Risque basé sur l'absence d'informations de caméra
    if has_exif and not camera_info.get("make") and not camera_info.get("model"):
        risk_score += 15
    
    # Limiter le score à 100
    return min(risk_score, 100)