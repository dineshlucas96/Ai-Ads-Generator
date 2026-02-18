import copy as copy_module
from agents.creative_agent import generate_copy, DEMO_COPY, _fill_template
import random

TONES = ["professional", "playful", "urgent", "emotional"]


def generate_variations(brief: dict, base_copy: dict) -> list:
    """
    Variation Agent: Produces multiple A/B test variations of the base creative.
    Generates one version per tone (professional, playful, urgent, emotional).
    """
    variations = []
    product_name = brief.get("product_name", "Our Product")
    audience = brief.get("audience", "customers")
    base_tone = base_copy.get("tone", "professional")

    for tone in TONES:
        if tone == base_tone:
            # Use the already-generated base copy for the primary tone
            variations.append({
                "tone": tone,
                "headline": base_copy["headline"],
                "body": base_copy["body"],
                "cta": base_copy["cta"],
                "is_primary": True,
                "performance_hint": _get_performance_hint(tone)
            })
        else:
            # Generate variation for this tone
            copy_data = DEMO_COPY[tone]
            headline = _fill_template(random.choice(copy_data["headline"]), product_name, audience)
            body = _fill_template(random.choice(copy_data["body"]), product_name, audience)
            cta = _fill_template(random.choice(copy_data["cta"]), product_name, audience)

            variations.append({
                "tone": tone,
                "headline": headline,
                "body": body,
                "cta": cta,
                "is_primary": False,
                "performance_hint": _get_performance_hint(tone)
            })

    # Sort so primary tone is first
    variations.sort(key=lambda v: (0 if v["is_primary"] else 1, TONES.index(v["tone"])))
    return variations


def _get_performance_hint(tone: str) -> dict:
    """Return typical performance characteristics for each tone."""
    hints = {
        "professional": {
            "best_for": "B2B, LinkedIn, decision-makers",
            "avg_ctr": "2.1%",
            "conversion": "High",
            "icon": "💼"
        },
        "playful": {
            "best_for": "Instagram, Gen Z, lifestyle brands",
            "avg_ctr": "3.4%",
            "conversion": "Medium",
            "icon": "🎉"
        },
        "urgent": {
            "best_for": "Retargeting, flash sales, limited offers",
            "avg_ctr": "4.2%",
            "conversion": "Very High",
            "icon": "⚡"
        },
        "emotional": {
            "best_for": "Facebook, storytelling, brand awareness",
            "avg_ctr": "2.8%",
            "conversion": "High",
            "icon": "💙"
        }
    }
    return hints.get(tone, hints["professional"])
