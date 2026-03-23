"""
Service d'analyse stéganographique.
Détecte les traces possibles de données cachées dans l'image.
"""

from typing import Dict, Any, List
import numpy as np
from PIL import Image
import io
from scipy import stats


def analyze_steganography(image_data: bytes) -> Dict[str, Any]:
    """
    Analyser une image pour détecter des traces de stéganographie
    
    Args:
        image_data: Données binaires de l'image
        
    Returns:
        Dictionnaire contenant les résultats de l'analyse stéganographique
    """
    
    results = {
        "suspicious": False,
        "lsb_analysis": {},
        "histogram_analysis": {},
        "statistical_tests": {},
        "noise_analysis": {},
        "anomalies": [],
        "risk_score": 0,
        "confidence": 0
    }
    
    try:
        # Ouvrir l'image
        image = Image.open(io.BytesIO(image_data))
        
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convertir en array numpy
        img_array = np.array(image)
        
        # Analyse des bits de poids faible (LSB)
        results["lsb_analysis"] = analyze_lsb(img_array)
        
        # Analyse de l'histogramme
        results["histogram_analysis"] = analyze_histogram(img_array)
        
        # Tests statistiques
        results["statistical_tests"] = perform_statistical_tests(img_array)
        
        # Analyse du bruit
        results["noise_analysis"] = analyze_noise(img_array)
        
        # Détecter les anomalies
        results["anomalies"] = detect_stego_anomalies(results)
        
        # Déterminer si suspect
        results["suspicious"] = len(results["anomalies"]) > 0
        
        # Calculer le score de risque
        results["risk_score"] = calculate_stego_risk_score(
            results["lsb_analysis"],
            results["histogram_analysis"],
            results["statistical_tests"],
            results["noise_analysis"],
            results["anomalies"]
        )
        
        # Calculer la confiance
        results["confidence"] = calculate_stego_confidence(results)
        
    except Exception as e:
        results["anomalies"].append(f"Erreur lors de l'analyse stéganographique: {str(e)}")
        results["risk_score"] = 20
    
    return results


def analyze_lsb(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Analyser les bits de poids faible (Least Significant Bits)
    
    La stéganographie LSB modifie les bits de poids faible des pixels
    pour y cacher des informations.
    
    Args:
        img_array: Array numpy de l'image
        
    Returns:
        Dictionnaire avec les résultats de l'analyse LSB
    """
    lsb_results = {
        "randomness_score": 0,
        "even_odd_ratio": {},
        "suspicious": False
    }
    
    try:
        # Extraire les bits de poids faible
        lsb_plane = img_array & 0x01
        
        # Calculer le score de randomité
        # Un LSB qui contient des données cachées tend à être aléatoire
        randomness = calculate_randomness(lsb_plane)
        lsb_results["randomness_score"] = randomness
        
        # Analyser le ratio pair/impair pour chaque canal
        channels = ['R', 'G', 'B']
        for i, channel in enumerate(channels):
            lsb_channel = lsb_plane[:, :, i].flatten()
            ones_count = np.sum(lsb_channel)
            total = len(lsb_channel)
            even_count = total - ones_count
            
            ratio = ones_count / total if total > 0 else 0.5
            lsb_results["even_odd_ratio"][channel] = {
                "even": even_count,
                "odd": ones_count,
                "ratio": ratio
            }
            
            # Un ratio proche de 0.5 peut indiquer des données cachées
            if 0.48 <= ratio <= 0.52:
                lsb_results["suspicious"] = True
        
    except Exception as e:
        lsb_results["error"] = str(e)
    
    return lsb_results


def analyze_histogram(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Analyser l'histogramme de l'image
    
    La stéganographie peut modifier l'histogramme de manière subtile.
    
    Args:
        img_array: Array numpy de l'image
        
    Returns:
        Dictionnaire avec les résultats de l'analyse d'histogramme
    """
    histogram_results = {
        "chi_square": 0,
        "p_value": 0,
        "suspicious": False
    }
    
    try:
        channels = ['R', 'G', 'B']
        chi_square_values = []
        p_values = []
        
        for i, channel in enumerate(channels):
            channel_data = img_array[:, :, i].flatten()
            
            # Calculer l'histogramme
            hist, _ = np.histogram(channel_data, bins=256, range=(0, 256))
            
            # Test du chi-carré pour vérifier l'uniformité
            # Une distribution uniforme peut indiquer des données cachées
            expected = np.full(256, len(channel_data) / 256)
            
            # Éviter les divisions par zéro
            expected[expected == 0] = 1
            
            chi_sq = np.sum((hist - expected) ** 2 / expected)
            p_val = 1 - stats.chi2.cdf(chi_sq, 255)
            
            chi_square_values.append(chi_sq)
            p_values.append(p_val)
        
        histogram_results["chi_square"] = np.mean(chi_square_values)
        histogram_results["p_value"] = np.mean(p_values)
        
        # Un p-value très bas peut indiquer des anomalies
        if histogram_results["p_value"] < 0.01:
            histogram_results["suspicious"] = True
        
    except Exception as e:
        histogram_results["error"] = str(e)
    
    return histogram_results


def perform_statistical_tests(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Effectuer des tests statistiques pour détecter la stéganographie
    
    Args:
        img_array: Array numpy de l'image
        
    Returns:
        Dictionnaire avec les résultats des tests statistiques
    """
    stat_results = {
        "kurtosis": {},
        "skewness": {},
        "mean": {},
        "std": {},
        "suspicious": False
    }
    
    try:
        channels = ['R', 'G', 'B']
        
        for i, channel in enumerate(channels):
            channel_data = img_array[:, :, i].flatten()
            
            # Calculer les statistiques
            stat_results["mean"][channel] = float(np.mean(channel_data))
            stat_results["std"][channel] = float(np.std(channel_data))
            stat_results["kurtosis"][channel] = float(stats.kurtosis(channel_data))
            stat_results["skewness"][channel] = float(stats.skew(channel_data))
            
            # Des valeurs de kurtosis extrêmes peuvent indiquer des anomalies
            if abs(stat_results["kurtosis"][channel]) > 10:
                stat_results["suspicious"] = True
        
    except Exception as e:
        stat_results["error"] = str(e)
    
    return stat_results


def analyze_noise(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Analyser le bruit dans l'image
    
    La stéganographie peut introduire un bruit non naturel.
    
    Args:
        img_array: Array numpy de l'image
        
    Returns:
        Dictionnaire avec les résultats de l'analyse du bruit
    """
    noise_results = {
        "noise_level": 0,
        "high_frequency_content": 0,
        "suspicious": False
    }
    
    try:
        # Calculer le gradient pour détecter le bruit haute fréquence
        gradient_x = np.diff(img_array, axis=1)
        gradient_y = np.diff(img_array, axis=0)
        
        # Calculer le niveau de bruit
        noise_x = np.std(gradient_x)
        noise_y = np.std(gradient_y)
        
        noise_results["noise_level"] = float((noise_x + noise_y) / 2)
        
        # Contenu haute fréquence
        high_freq = np.sqrt(gradient_x ** 2 + gradient_y ** 2)
        noise_results["high_frequency_content"] = float(np.mean(high_freq))
        
        # Un niveau de bruit élevé peut indiquer des données cachées
        if noise_results["noise_level"] > 30:
            noise_results["suspicious"] = True
        
    except Exception as e:
        noise_results["error"] = str(e)
    
    return noise_results


def calculate_randomness(data: np.ndarray) -> float:
    """
    Calculer un score de randomité pour les données
    
    Args:
        data: Array numpy
        
    Returns:
        Score de randomité (0-1)
    """
    try:
        # Test deRuns pour la randomité
        flattened = data.flatten()
        runs = 0
        current = flattened[0]
        
        for value in flattened[1:]:
            if value != current:
                runs += 1
                current = value
        
        # Normaliser
        expected_runs = 2 * len(flattened) * 0.5 * 0.5
        actual_runs = runs
        
        # Score plus proche de 1 = plus aléatoire
        score = min(abs(actual_runs - expected_runs) / expected_runs, 1.0)
        
        return float(score)
        
    except:
        return 0.0


def detect_stego_anomalies(results: Dict[str, Any]) -> List[str]:
    """
    Détecter les anomalies de stéganographie
    
    Args:
        results: Résultats de l'analyse
        
    Returns:
        Liste des anomalies détectées
    """
    anomalies = []
    
    # Anomalies LSB
    if results.get("lsb_analysis", {}).get("suspicious", False):
        anomalies.append("Pattern suspect détecté dans les bits de poids faible (LSB)")
    
    # Anomalies histogramme
    if results.get("histogram_analysis", {}).get("suspicious", False):
        anomalies.append("Distribution anormale dans l'histogramme")
    
    # Anomalies statistiques
    if results.get("statistical_tests", {}).get("suspicious", False):
        anomalies.append("Anomalies statistiques détectées")
    
    # Anomalies bruit
    if results.get("noise_analysis", {}).get("suspicious", False):
        anomalies.append("Niveau de bruit anormalement élevé")
    
    # Randomité élevée
    lsb_randomness = results.get("lsb_analysis", {}).get("randomness_score", 0)
    if lsb_randomness > 0.8:
        anomalies.append("Haute randomité détectée dans les LSB - possible stéganographie")
    
    return anomalies


def calculate_stego_risk_score(
    lsb_analysis: Dict[str, Any],
    histogram_analysis: Dict[str, Any],
    statistical_tests: Dict[str, Any],
    noise_analysis: Dict[str, Any],
    anomalies: List[str]
) -> int:
    """
    Calculer un score de risque basé sur l'analyse stéganographique
    
    Args:
        lsb_analysis: Résultats LSB
        histogram_analysis: Résultats histogramme
        statistical_tests: Résultats tests statistiques
        noise_analysis: Résultats bruit
        anomalies: Liste des anomalies
        
    Returns:
        Score de risque (0-100)
    """
    risk_score = 0
    
    # Risque basé sur les anomalies
    risk_score += len(anomalies) * 20
    
    # Risque basé sur l'analyse LSB
    if lsb_analysis.get("suspicious", False):
        risk_score += 25
    
    # Risque basé sur l'histogramme
    if histogram_analysis.get("suspicious", False):
        risk_score += 15
    
    # Risque basé sur les tests statistiques
    if statistical_tests.get("suspicious", False):
        risk_score += 15
    
    # Risque basé sur le bruit
    if noise_analysis.get("suspicious", False):
        risk_score += 15
    
    # Limiter le score à 100
    return min(risk_score, 100)


def calculate_stego_confidence(results: Dict[str, Any]) -> float:
    """
    Calculer la confiance de l'analyse stéganographique
    
    Args:
        results: Résultats de l'analyse
        
    Returns:
        Score de confiance (0-1)
    """
    # Nombre d'indicateurs suspects
    suspicious_indicators = 0
    total_indicators = 4
    
    if results.get("lsb_analysis", {}).get("suspicious", False):
        suspicious_indicators += 1
    if results.get("histogram_analysis", {}).get("suspicious", False):
        suspicious_indicators += 1
    if results.get("statistical_tests", {}).get("suspicious", False):
        suspicious_indicators += 1
    if results.get("noise_analysis", {}).get("suspicious", False):
        suspicious_indicators += 1
    
    # Confiance basée sur le nombre d'anomalies
    anomaly_count = len(results.get("anomalies", []))
    
    # Combiner les facteurs
    indicator_confidence = suspicious_indicators / total_indicators if total_indicators > 0 else 0
    anomaly_confidence = min(anomaly_count / 3, 1.0)
    
    overall_confidence = (indicator_confidence + anomaly_confidence) / 2
    
    return round(overall_confidence, 2)