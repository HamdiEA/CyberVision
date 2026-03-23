"""
Service de chat visuel OpenRouter pour l'analyse forensique d'images.
"""

from typing import Dict, Any
import os
import requests
import re
from pathlib import Path
from dotenv import load_dotenv

# Charger le fichier .env depuis la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH, override=True)


def _format_context(analysis: Dict[str, Any]) -> str:
    # Transforme les résultats forensiques en texte compact pour le prompt.
    integrity = analysis.get("integrity", {})
    modules = analysis.get("modules", {})
    exif = modules.get("exif", {})
    structure = modules.get("structure", {})
    stego = modules.get("steganography", {})
    ai_vis = modules.get("ai_visual", {})

    lines = [
        f"Score d'intégrité: {integrity.get('score', '?')}/100",
        f"Niveau de risque: {integrity.get('risk_level', '?')}",
        f"Confiance: {integrity.get('confidence', '?')}%",
        f"Résumé: {integrity.get('summary', '')}",
        "Anomalies EXIF: " + "; ".join(exif.get("anomalies", []) or ["aucune"]),
        "Anomalies structurelles: " + "; ".join(structure.get("anomalies", []) or ["aucune"]),
        "Anomalies stéganographiques: " + "; ".join(stego.get("anomalies", []) or ["aucune"]),
        "Notes visuelles IA: " + "; ".join(ai_vis.get("visual_inconsistencies", []) or [ai_vis.get("explanation", "") or "aucune"]),
    ]
    return "\n".join(lines)


def _local_fallback(question: str, analysis: Dict[str, Any]) -> str:
    # Retourne une réponse locale simple si l'IA distante est indisponible.
    integrity = analysis.get("integrity", {})
    score = integrity.get("score")
    risk = integrity.get("risk_level")
    summary = integrity.get("summary") or ""
    parts = [f"Question: {question}"]
    if score is not None:
        parts.append(f"Score d'intégrité: {score}/100")
    if risk:
        parts.append(f"Niveau de risque: {risk}")
    if summary:
        parts.append(f"Résumé: {summary}")
    parts.append("(Analyse locale - vision IA indisponible)")
    return " | ".join(parts)


def _local_fallback_with_reason(question: str, analysis: Dict[str, Any], reason: str | None) -> str:
    # Ajoute la raison d'échec technique à la réponse locale.
    base = _local_fallback(question, analysis)
    if not reason:
        return base
    return f"{base} | (Erreur IA: {reason})"


def generate_chat_answer(
    question: str,
    analysis: Dict[str, Any],
    image_url: str | None = None,
    image_data: Dict[str, str] | None = None,
) -> str:
    # Appelle OpenRouter pour générer une réponse forensique guidée par l'image.
    """
    Générer une réponse via l'API OpenRouter chat/completions.
    Analyse l'image pour identifier les modifications et zones suspectes.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    base_url = os.getenv("OPENROUTER_API_BASE_URL", "https://openrouter.ai/api/v1")
    fallback_models_raw = os.getenv(
        "OPENROUTER_FALLBACK_MODELS",
        "google/gemini-2.0-flash-001,meta-llama/llama-3.2-11b-vision-instruct",
    )

    has_key = bool(api_key and len(api_key) > 10)
    print(f"\n[OpenRouter Vision] Démarrage de l'analyse...")
    print(f"  Modèle principal: {model_name}")
    print(f"  Clé API présente: {has_key}")
    
    if not has_key:
        print(f"[OpenRouter] ERREUR: clé API absente")
        return _local_fallback("Clé API manquante", analysis or {})

    try:
        context = _format_context(analysis or {})
        
        # Construire un prompt compatible chat/completions pour OpenRouter.
        system_prompt = (
            "Tu es un expert en analyse forensique d'images numériques. "
            "Réponds exclusivement en français. "
            "À partir de l'image et de ses métadonnées forensiques, identifie les manipulations. "
            "Sois précis sur OÙ, QUOI et COMMENT."
        )

        user_text = (
            f"Question: {question}\n\n"
            "Identifie précisément:\n"
            "1) OÙ les modifications apparaissent (coins, centre, contours, visages, objets, etc.)\n"
            "2) QUEL type de modification (Photoshop, génération IA, deepfake, filtre, artefacts de compression, etc.)\n"
            "3) COMMENT tu le détectes (artefacts, lumière, bords, texture, flou, dérive des couleurs)\n"
            "4) Niveau de confiance (élevé/moyen/faible)\n\n"
            f"Métadonnées forensiques:\n{context}"
        )

        user_content: list[dict[str, Any]] = [{"type": "text", "text": user_text}]

        # Joindre l'image dans un bloc image_url compatible OpenAI.
        if image_data and "base64" in image_data and len(image_data["base64"]) > 100:
            mime_type = image_data.get("mime_type", "image/jpeg")
            data_uri = f"data:{mime_type};base64,{image_data['base64']}"
            user_content.append({
                "type": "image_url",
                "image_url": {"url": data_uri},
            })
            print(f"[OpenRouter] Image jointe (data URI, {len(image_data['base64'])} caractères)")
        elif image_url:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": image_url},
            })
            print(f"[OpenRouter] Image jointe (URL)")
        else:
            print(f"[OpenRouter] AVERTISSEMENT: aucune image fournie")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:5173"),
            "X-Title": os.getenv("OPENROUTER_APP_NAME", "CyberVision"),
        }

        candidate_models = [model_name]
        for m in [x.strip() for x in fallback_models_raw.split(",") if x.strip()]:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error: str | None = None

        # Garder des réponses courtes pour rester économiques selon les crédits OpenRouter.
        base_payload = {
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 600,
        }

        for current_model in candidate_models:
            payload = {
                **base_payload,
                "model": current_model,
            }
            print(f"[OpenRouter] Tentative avec le modèle: {current_model}")
            resp = requests.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
            )
            print(f"[OpenRouter] Statut de réponse: {resp.status_code}")

            if resp.status_code == 402:
                try:
                    error_data = resp.json()
                    err_msg = str(error_data.get("error", {}).get("message", ""))
                except Exception:
                    err_msg = resp.text

                affordable_match = re.search(r"afford\s+(\d+)", err_msg)
                affordable_tokens = int(affordable_match.group(1)) if affordable_match else 256
                retry_tokens = max(128, min(affordable_tokens, 400))
                print(f"[OpenRouter] Nouvelle tentative sur {current_model} avec max_tokens={retry_tokens}")

                payload["max_tokens"] = retry_tokens
                resp = requests.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120,
                )
                print(f"[OpenRouter] Statut après nouvelle tentative: {resp.status_code}")

            if resp.status_code != 200:
                error_text = resp.text[:300]
                last_error = f"{current_model} HTTP {resp.status_code}: {error_text}"
                print(f"[OpenRouter] ERREUR {last_error}")
                continue

            data = resp.json()
            choices = data.get("choices") or []
            print(f"[OpenRouter] Nombre de choix: {len(choices)}")
            if choices:
                choice = choices[0] or {}
                message = choice.get("message", {}) or {}
                content = message.get("content")
                if isinstance(content, str):
                    text = content.strip()
                    if text:
                        print(f"[OpenRouter] SUCCÈS depuis {current_model}")
                        return text
                content = content or []
                parts = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") in ("text", "output_text") and block.get("text"):
                            parts.append(block.get("text"))
                if parts:
                    text = "\n".join(parts).strip()
                    if text:
                        print(f"[OpenRouter] SUCCÈS depuis {current_model}")
                        return text

            last_error = f"{current_model}: empty response content"

        print(f"[OpenRouter] Aucun modèle n'a retourné de contenu exploitable")
        return _local_fallback_with_reason(question, analysis, last_error)
        
    except Exception as exc:
        print(f"[OpenRouter] TYPE D'EXCEPTION: {type(exc).__name__}")
        print(f"[OpenRouter] EXCEPTION: {exc}")
        import traceback
        traceback.print_exc()
        return _local_fallback_with_reason(question, analysis or {}, str(exc))
