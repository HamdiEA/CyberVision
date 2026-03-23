"""
Fonctions utilitaires du backend.
Détection de type MIME pour fiabiliser les contrôles d'upload.
"""

try:
    import magic  # type: ignore
except ImportError:  # pragma: no cover - handled gracefully at runtime
    magic = None


def sniff_mime_type(data: bytes) -> str | None:
    # Détecte le vrai type MIME d'un fichier binaire.
    """
    Détecter le type MIME réel en utilisant python-magic si disponible.

    Args:
        data: Données binaires du fichier

    Returns:
        Chaîne MIME (ex: "image/jpeg") ou None si la détection n'est pas possible
    """
    if not magic:
        return None
    try:
        detector = magic.Magic(mime=True)
        return detector.from_buffer(data)
    except Exception:
        return None
