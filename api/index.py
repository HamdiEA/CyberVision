"""
Point d'entree ASGI Vercel pour CyberVision.
Monte le backend FastAPI sur /api et / pour compatibilite.
"""

from fastapi import FastAPI

from backend.main import app as backend_app

app = FastAPI(title="CyberVision Vercel Gateway")

# Route principale des fonctions Vercel.
app.mount("/api", backend_app)

# Garde aussi les routes directes pour les tests locaux.
app.mount("/", backend_app)
