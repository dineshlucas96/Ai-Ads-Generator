import os
import random
from dotenv import load_dotenv

load_dotenv()

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Curated Unsplash image collections by category (free, no auth needed)
DEMO_IMAGES = {
    "tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&q=80",
        "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800&q=80",
    ],
    "lifestyle": [
        "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80",
        "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&q=80",
        "https://images.unsplash.com/photo-1511988617509-a57c8a288659?w=800&q=80",
    ],
    "food": [
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
        "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&q=80",
    ],
    "fashion": [
        "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80",
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&q=80",
        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=800&q=80",
    ],
    "fitness": [
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&q=80",
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80",
    ],
    "default": [
        "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&q=80",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
        "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&q=80",
    ]
}


def _detect_category(brief: dict) -> str:
    """Detect image category from brief keywords."""
    text = f"{brief.get('product_name', '')} {brief.get('description', '')}".lower()
    if any(k in text for k in ["tech", "app", "software", "device", "phone", "laptop", "computer"]):
        return "tech"
    if any(k in text for k in ["food", "drink", "eat", "restaurant", "meal", "snack", "beverage"]):
        return "food"
    if any(k in text for k in ["fashion", "cloth", "wear", "style", "outfit", "dress", "shoe"]):
        return "fashion"
    if any(k in text for k in ["fit", "gym", "workout", "health", "sport", "exercise", "yoga"]):
        return "fitness"
    if any(k in text for k in ["life", "home", "family", "travel", "people", "social"]):
        return "lifestyle"
    return "default"


def generate_images(brief: dict, copy: dict) -> list:
    """
    Design Agent: Generates visual assets for the ad creative.
    Uses DALL-E 3 if available, otherwise returns curated Unsplash images.
    """
    if not DEMO_MODE and OPENAI_API_KEY:
        return _generate_images_dalle(brief, copy)

    # Demo mode: return curated Unsplash images
    category = _detect_category(brief)
    images = DEMO_IMAGES.get(category, DEMO_IMAGES["default"])
    selected = random.sample(images, min(3, len(images)))

    return [
        {
            "url": url,
            "prompt": f"Ad visual for {brief.get('product_name')} targeting {brief.get('audience')}",
            "style": category,
            "index": i + 1
        }
        for i, url in enumerate(selected)
    ]


def _generate_images_dalle(brief: dict, copy: dict) -> list:
    """Generate images using DALL-E 3."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = (
            f"Professional advertising photo for {brief.get('product_name')}. "
            f"{brief.get('description')}. "
            f"Target audience: {brief.get('audience')}. "
            f"Style: modern, clean, high-quality commercial photography. "
            f"No text overlay."
        )

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        return [{
            "url": response.data[0].url,
            "prompt": prompt,
            "style": "ai-generated",
            "index": 1
        }]
    except Exception as e:
        print(f"DALL-E error: {e}, falling back to demo images")
        return generate_images(brief, copy)
