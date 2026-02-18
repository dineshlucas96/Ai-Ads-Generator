import uuid
import time
import requests as http_requests
from flask import Blueprint, request, jsonify, Response
from agents.creative_agent import generate_copy
from agents.design_agent import generate_images
from agents.variation_agent import generate_variations
from agents.platform_agent import adapt_for_platforms

api_bp = Blueprint("api", __name__, url_prefix="/api")

# In-memory job store (use Redis/DB in production)
jobs = {}


@api_bp.route("/generate", methods=["POST"])
def generate():
    """
    Main generation endpoint. Triggers all 4 agents sequentially.
    Body: { product_name, description, audience, tone, platforms[] }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    required = ["product_name", "description", "audience"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    brief = {
        "product_name": data.get("product_name", "").strip(),
        "description": data.get("description", "").strip(),
        "audience": data.get("audience", "").strip(),
        "tone": data.get("tone", "professional"),
        "platforms": data.get("platforms", ["instagram", "facebook", "twitter", "linkedin"])
    }

    try:
        # Agent 1: Creative Agent — generate copy
        copy = generate_copy(brief)

        # Agent 2: Design Agent — generate images
        images = generate_images(brief, copy)

        # Agent 3: Variation Agent — generate A/B variations
        variations = generate_variations(brief, copy)

        # Agent 4: Platform Agent — adapt for platforms
        platforms = adapt_for_platforms(brief, copy, images, brief["platforms"])

        result = {
            "job_id": str(uuid.uuid4()),
            "brief": brief,
            "copy": copy,
            "images": images,
            "variations": variations,
            "platforms": platforms,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/refine", methods=["POST"])
def refine():
    """
    Conversational refinement endpoint.
    Body: { message, current_copy, brief }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    message = data.get("message", "").lower()
    brief = data.get("brief", {})
    current_copy = data.get("current_copy", {})

    # Parse refinement intent from message
    new_tone = _detect_tone_from_message(message)
    if new_tone:
        brief["tone"] = new_tone

    # Regenerate copy with updated brief
    new_copy = generate_copy(brief)
    new_variations = generate_variations(brief, new_copy)

    return jsonify({
        "copy": new_copy,
        "variations": new_variations,
        "refinement_applied": f"Tone adjusted to '{new_tone}'" if new_tone else "Copy refreshed",
        "message": _generate_agent_response(message, new_copy)
    }), 200


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "agents": ["creative", "design", "variation", "platform"]}), 200


@api_bp.route("/download-image", methods=["GET"])
def download_image():
    """
    Proxy endpoint to download cross-origin images.
    Query params: url (image URL), filename (desired filename)
    """
    image_url = request.args.get("url", "")
    filename = request.args.get("filename", "ad-image.jpg")

    if not image_url:
        return jsonify({"error": "url parameter required"}), 400

    # Only allow known image domains for security
    allowed_domains = ["images.unsplash.com", "oaidalleapiprodscus.blob.core.windows.net"]
    from urllib.parse import urlparse
    parsed = urlparse(image_url)
    if not any(parsed.netloc.endswith(d) for d in allowed_domains):
        return jsonify({"error": "Image domain not allowed"}), 403

    try:
        resp = http_requests.get(image_url, timeout=15, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "image/jpeg")

        return Response(
            resp.content,
            headers={
                "Content-Type": content_type,
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        return jsonify({"error": f"Failed to fetch image: {str(e)}"}), 500


def _detect_tone_from_message(message: str) -> str:
    """Detect desired tone from user's refinement message."""
    tone_keywords = {
        "professional": ["professional", "formal", "business", "corporate", "serious", "b2b"],
        "playful": ["playful", "fun", "funny", "casual", "light", "humorous", "witty", "young"],
        "urgent": ["urgent", "urgency", "scarcity", "limited", "hurry", "fast", "quick", "now", "sale"],
        "emotional": ["emotional", "heartfelt", "touching", "warm", "inspiring", "story", "feel"]
    }
    for tone, keywords in tone_keywords.items():
        if any(kw in message for kw in keywords):
            return tone
    return None


def _generate_agent_response(message: str, new_copy: dict) -> str:
    """Generate a friendly agent response to the refinement request."""
    responses = [
        f"✅ Got it! I've updated the copy to match your request. The new headline is: \"{new_copy['headline']}\"",
        f"🎯 Done! I've refined the creative based on your feedback. Check out the updated version!",
        f"✨ Updated! Here's the refreshed copy with your adjustments applied.",
        f"🚀 Refined! The new headline reads: \"{new_copy['headline']}\" — let me know if you'd like more changes!"
    ]
    import random
    return random.choice(responses)
