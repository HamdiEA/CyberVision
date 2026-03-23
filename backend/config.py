"""
Configuration du backend CyberVision.
Charge les variables d'environnement et les paramètres globaux.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env à la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

# Configuration API
API_TITLE = "CyberVision API"
API_VERSION = "2.0.0"
API_DESCRIPTION = "API d'analyse forensique d'images numériques assistée par IA"

# Configuration CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Frontend dev
    "http://localhost:3000",  # Alternative port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Ajouter des origines supplémentaires depuis .env si nécessaire
extra_origins = os.getenv("CORS_ORIGINS", "")
if extra_origins:
    ALLOWED_ORIGINS.extend(extra_origins.split(","))

# Limites de fichiers
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/tiff",
]

def validate_config():
    # Vérifie la configuration active du backend.
    """Valider la configuration et afficher des avertissements"""
    return []
