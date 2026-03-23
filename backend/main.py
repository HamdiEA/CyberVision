"""
Application principale du backend CyberVision.
Expose les routes API d'analyse forensique.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64

try:
    from .config import (
        API_TITLE, API_VERSION, API_DESCRIPTION,
        ALLOWED_ORIGINS, MAX_FILE_SIZE, ALLOWED_EXTENSIONS,
        validate_config
    )
    from .services.analysis_engine import analyze_image, format_results_for_frontend
    from .services.chat_ai import generate_chat_answer
    from .utils.helpers import sniff_mime_type
except ImportError:
    from config import (
        API_TITLE, API_VERSION, API_DESCRIPTION,
        ALLOWED_ORIGINS, MAX_FILE_SIZE, ALLOWED_EXTENSIONS,
        validate_config
    )
    from services.analysis_engine import analyze_image, format_results_for_frontend
    from services.chat_ai import generate_chat_answer
    from utils.helpers import sniff_mime_type


class ChatRequest(BaseModel):
    question: str
    imageUrl: str | None = None
    imageBase64: str | None = None  # Image encodée en base64 pour l'analyse visuelle
    imageMimeType: str | None = None  # Type MIME de l'image
    analysis: dict | None = None

# Créer l'application FastAPI
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes de santé et configuration
@app.get("/")
async def root():
    # Retourne les informations de base de l'API.
    """Route racine - Informations sur l'API"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    # Retourne l'etat de sante du service.
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "api_configured": True
    }


@app.get("/config")
async def get_api_config():
    # Retourne les limites et options de configuration actives.
    """Obtenir la configuration de l'API"""
    warnings = validate_config()
    return {
        "max_file_size": MAX_FILE_SIZE,
        "allowed_extensions": ALLOWED_EXTENSIONS,
        "warnings": warnings
    }


@app.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    # Repond aux questions utilisateur a partir du contexte d'analyse.
    print(f"\n[CHAT ENDPOINT] Requête reçue")
    """Répondre à une question utilisateur sur l'image analysée."""
    question = payload.question.strip()
    analysis = payload.analysis or {}
    
    print(f"[CHAT] Question: {question[:100]}...")
    print(f"[CHAT] Base64 image présent: {bool(payload.imageBase64)}")
    if payload.imageBase64:
        print(f"[CHAT] Longueur base64: {len(payload.imageBase64)}")
    print(f"[CHAT] Type MIME: {payload.imageMimeType}")

    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question manquante")

    # Transmettre les données image (base64 + type MIME) pour l'analyse visuelle.
    image_data = None
    if payload.imageBase64 and payload.imageMimeType:
        image_data = {
            "base64": payload.imageBase64,
            "mime_type": payload.imageMimeType,
        }

    answer = generate_chat_answer(question, analysis, payload.imageUrl, image_data)
    print(f"[CHAT] Longueur de réponse: {len(answer)}")
    return {"answer": answer}


# Routes d'analyse d'images
@app.post("/analyze")
async def analyze_uploaded_image(
    file: UploadFile = File(...)
):
    # Lance l'analyse forensique complete pour une image envoyee.
    """
    Analyser une image uploadée
    
    Args:
        file: Fichier image à analyser
        token: Token d'authentification (optionnel)
        
    Returns:
        Résultats de l'analyse forensique
    """
    
    # Lire le contenu du fichier
    file_content = await file.read()

    # Vérifier la taille du fichier
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop volumineux. Taille maximale: {MAX_FILE_SIZE / (1024*1024):.1f} MB"
        )

    # Vérifier le type de fichier avec python-magic (détection réelle)
    detected_mime = sniff_mime_type(file_content)
    content_type = detected_mime or file.content_type
    if content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Type de fichier non supporté ({content_type or 'inconnu'}). "
                f"Types acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        )
    
    # Effectuer l'analyse
    results = await analyze_image(file_content, file.filename)
    
    # Formater les résultats pour le frontend
    formatted_results = format_results_for_frontend(results)

    # Générer automatiquement une interprétation IA à partir des résultats forensiques
    ai_question = (
        "À partir de cette analyse forensique, quel est le problème le plus probable de cette image ? "
        "Donne un exemple concret de manipulation possible et explique brièvement pourquoi."
    )
    image_data = {
        "base64": base64.b64encode(file_content).decode("utf-8"),
        "mime_type": content_type or "image/jpeg",
    }
    formatted_results["ai_interpretation"] = generate_chat_answer(
        ai_question,
        formatted_results,
        image_data=image_data,
    )
    
    return formatted_results


# Gestion des erreurs
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    # Formate les erreurs HTTP pour le frontend.
    """Gestionnaire d'exceptions HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    # Capture les erreurs inattendues avec une reponse standard.
    """Gestionnaire d'exceptions générales"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "details": str(exc)
        }
    )


# Nettoyage des sessions expirées (toutes les heures)
@app.on_event("startup")
async def startup_event():
    # Initialise le backend et affiche l'etat de configuration.
    """Événement de démarrage"""
    print(f"{API_TITLE} v{API_VERSION} démarré")
    print(f"Description: {API_DESCRIPTION}")
    
    # Afficher les avertissements de configuration
    warnings = validate_config()
    if warnings:
        print("Avertissements de configuration:")
        for warning in warnings:
            print(f"   - {warning}")
    else:
        print("Configuration OK")
    
    print(f"🌐 Origines CORS autorisées: {', '.join(ALLOWED_ORIGINS)}")
    print(f"📏 Taille maximale des fichiers: {MAX_FILE_SIZE / (1024*1024):.1f} MB")


@app.on_event("shutdown")
async def shutdown_event():
    # Journalise l'arret du backend.
    """Événement d'arrêt"""
    print(f"{API_TITLE} arrêté")


if __name__ == "__main__":
    import uvicorn

    # Démarrer le serveur
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )