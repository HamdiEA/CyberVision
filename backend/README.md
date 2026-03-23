# CyberVision Backend

Backend Python FastAPI pour l'analyse forensique d'images numériques.

## Vue d'ensemble

Ce backend fournit une API REST pour analyser les images et détecter :
- **Métadonnées EXIF** : Extraction et validation
- **Structure de fichier** : Vérification d'intégrité
- **Stéganographie** : Détection de données cachées
- **Analyse visuelle** : Détection de retouches et incohérences visuelles

## Architecture

```
backend/
├── main.py                    # Point d'entrée FastAPI
├── config.py                  # Configuration
├── services/                  # Modules d'analyse
│   ├── exif_analysis.py      # Analyse EXIF
│   ├── structure_analysis.py # Analyse structurelle
│   ├── stego_analysis.py     # Détection stéganographie
│   ├── ai_analysis.py        # Analyse visuelle automatisée
│   └── risk_calculator.py    # Calcul score d'intégrité
├── utils/                     # Utilitaires
│   └── helpers.py
├── requirements.txt           # Dépendances Python
└── .env.example              # Template variables d'environnement
```

## Installation

### Prérequis
- **Python 3.10+** ([télécharger](https://python.org/))
- **pip** (inclus avec Python)

### Étapes d'installation

```bash
# 1. Aller dans le dossier backend
cd backend

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv

# 3. Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer les variables d'environnement si nécessaire
copy .env.example .env
```

## Démarrage

### Mode développement

```bash
# Avec uvicorn directement
uvicorn main:app --reload --port 8000

# Ou avec Python
python main.py
```

Le serveur sera accessible sur `http://localhost:8000`

### Documentation API

Une fois le serveur démarré, accéder à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 📡 Endpoints API

### `GET /`
Health check et informations sur l'API

**Réponse:**
```json
{
  "message": "CyberVision API - Forensic Image Analysis",
  "version": "2.0.0",
  "status": "operational"
}
```

### `POST /api/analyze`
Analyser une image

**Request:**
- Content-Type: `multipart/form-data`
- Body: `image` (file - JPEG, PNG, BMP)

**Réponse:**
```json
{
  "timestamp": "2026-01-21T10:30:00",
  "file_info": {
    "filename": "photo.jpg",
    "size": 1048576,
    "format": "jpeg",
    "dimensions": [1920, 1080]
  },
  "analysis": {
    "exif": { ... },
    "structure": { ... },
    "steganography": { ... },
    "visual_ai": { ... }
  },
  "integrity_score": 75,
  "risk_level": "warning",
  "confidence": 0.85,
  "summary": "⚠️ L'image présente quelques anomalies mineures...",
  "recommendations": [...]
}
```

### `GET /api/formats`
Liste des formats d'images supportés

**Réponse:**
```json
{
  "supported_formats": ["JPEG", "PNG", "BMP"],
  "max_file_size": "10 MB",
  "mime_types": ["image/jpeg", "image/png", "image/bmp"]
}
```

## 🔬 Modules d'analyse

### 1. Analyse EXIF (`exif_analysis.py`)
- Extraction des métadonnées (caméra, dates, GPS)
- Détection d'anomalies (dates incohérentes, logiciels d'édition)
- Score de risque basé sur les anomalies

### 2. Analyse Structurelle (`structure_analysis.py`)
- Vérification des magic numbers (headers)
- Calcul de l'entropie des données
- Détection d'incohérences de format

### 3. Détection Stéganographie (`stego_analysis.py`)
- Analyse LSB (Least Significant Bit)
- Test statistique chi-carré
- Détection de patterns anormaux

### 4. Analyse visuelle (`ai_analysis.py`)
- Détection de retouches visuelles
- Identification d'incohérences d'éclairage/ombres
- Génération d'explications en langage naturel

### 5. Calculateur de Risque (`risk_calculator.py`)
- Agrégation des résultats de tous les modules
- Calcul du score d'intégrité (0-100)
- Détermination du niveau de risque
- Génération de recommandations

## Score d'intégrité

Le système calcule un score de 0 à 100 :

```
85-100  AUTHENTIQUE  (safe)       - Image probablement originale
70-84   ATTENTION    (warning)    - Anomalies mineures
40-69   SUSPECT      (suspect)    - Modifications probables
0-39    CRITIQUE     (critical)   - Image fortement altérée
```

## 🔐 Sécurité

- ✅ Validation stricte des types de fichiers
- ✅ Limite de taille (10 MB)
- ✅ Pas de stockage permanent des images
- ✅ Nettoyage automatique après analyse
- ✅ Protection CORS configurée

## 🐛 Dépannage

### Erreur: `ModuleNotFoundError`
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur: `Gemini API key not configured`
```bash
# Vérifier que .env existe et contient la clé
cat .env  # Linux/Mac
type .env  # Windows
```

### Erreur: `Port already in use`
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

## 📦 Dépendances principales

- **FastAPI** : Framework web moderne
- **Pillow** : Manipulation d'images
- **OpenCV** : Vision par ordinateur
- **NumPy** : Calculs numériques
- **SciPy** : Analyses statistiques
- **google-generativeai** : API Gemini
- **piexifify** : Métadonnées EXIF
- **python-magic** : Détection de types de fichiers

## 🧪 Tests

```bash
# Tester l'endpoint d'analyse avec curl
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/path/to/image.jpg"

# Vérifier le health check
curl http://localhost:8000/
```

## 📝 Logs

Le backend affiche des logs détaillés :

```
[INFO] Analyse de l'image: photo.jpg
[SUCCESS] Analyse terminée - Score: 85/100
[WARNING] Gemini API key not configured - using fallback
[ERROR] Erreur lors de l'analyse EXIF: ...
```

## 🚀 Déploiement en production

### Render / Railway

```bash
# Commande de démarrage
uvicorn main:app --host 0.0.0.0 --port $PORT

# Variables d'environnement à configurer
GEMINI_API_KEY=<votre_clé>
PORT=8000
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📄 Licence

Projet académique - Année universitaire 2025/2026  
**Auteur:** Me EL ABED Hamdi

---

**Version:** 2.0.0 | **Dernière mise à jour:** Janvier 2026
