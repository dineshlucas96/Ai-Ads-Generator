import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

DEMO_COPY = {
    "professional": {
        "headline": [
            "Elevate Your Everyday. Discover {product}.",
            "The Smart Choice for {audience}. Meet {product}.",
            "Performance Meets Purpose — {product}."
        ],
        "body": [
            "Designed for those who demand more, {product} delivers unmatched quality and reliability. Join thousands of satisfied customers who've made the switch.",
            "{product} is engineered for {audience} who refuse to compromise. Experience the difference that thoughtful design makes.",
            "When performance matters, professionals choose {product}. Built to exceed expectations, every single time."
        ],
        "cta": ["Shop Now", "Learn More", "Get Started Today", "Explore {product}"]
    },
    "playful": {
        "headline": [
            "Life's Too Short for Boring. Try {product}! 🎉",
            "Say Hello to Your New Favorite Thing: {product} ✨",
            "Fun Just Got an Upgrade — {product} is Here! 🚀"
        ],
        "body": [
            "Why settle for ordinary when {product} makes everything extraordinary? Your {audience} friends are already obsessed — don't miss out!",
            "Spoiler alert: once you try {product}, there's no going back. It's that good. Seriously. 😍",
            "{product} is the upgrade you didn't know you needed. Perfect for {audience} who love to stand out from the crowd!"
        ],
        "cta": ["Grab Yours Now! 🛒", "I Want One!", "Let's Go! 🎯", "Yes, Please!"]
    },
    "urgent": {
        "headline": [
            "Limited Time: {product} at an Unbeatable Price",
            "Don't Miss Out — {product} Selling Fast!",
            "Last Chance: {product} Offer Ends Soon ⏰"
        ],
        "body": [
            "This exclusive offer on {product} won't last. {audience} are snapping these up fast — secure yours before it's gone.",
            "Only a few left! {product} has been flying off the shelves. Act now and get yours before stock runs out.",
            "Flash sale ending soon. {product} — the solution {audience} have been waiting for — now at its lowest price ever."
        ],
        "cta": ["Claim Your Deal Now", "Buy Before It's Gone", "Order Now — Limited Stock", "Get It Today"]
    },
    "emotional": {
        "headline": [
            "{product}: Because You Deserve the Best",
            "For the Moments That Matter — {product}",
            "Give Yourself (or Someone You Love) {product} 💙"
        ],
        "body": [
            "Some things just make life better. {product} is one of them. Crafted with care for {audience} who appreciate the finer things.",
            "Every day is an opportunity to live better. {product} helps {audience} do exactly that — one moment at a time.",
            "The people you love deserve the best. {product} is a gift that keeps giving, bringing joy to {audience} everywhere."
        ],
        "cta": ["Start Your Journey", "Feel the Difference", "Make Someone Happy", "Shop with Heart"]
    }
}


def _fill_template(text, product_name, audience):
    return text.replace("{product}", product_name).replace("{audience}", audience)


def generate_copy(brief: dict) -> dict:
    """
    Creative Agent: Generates ad copy from a product brief.
    Uses OpenAI GPT-4 if available, otherwise returns demo copy.
    """
    product_name = brief.get("product_name", "Our Product")
    description = brief.get("description", "")
    audience = brief.get("audience", "customers")
    tone = brief.get("tone", "professional")

    if not DEMO_MODE and OPENAI_API_KEY:
        return _generate_copy_openai(brief)

    # Demo mode: return realistic mock copy
    tone_key = tone if tone in DEMO_COPY else "professional"
    copy_data = DEMO_COPY[tone_key]

    headline = _fill_template(random.choice(copy_data["headline"]), product_name, audience)
    body = _fill_template(random.choice(copy_data["body"]), product_name, audience)
    cta = _fill_template(random.choice(copy_data["cta"]), product_name, audience)

    return {
        "headline": headline,
        "body": body,
        "cta": cta,
        "tone": tone_key,
        "product_name": product_name,
        "audience": audience
    }


def _generate_copy_openai(brief: dict) -> dict:
    """Generate copy using OpenAI GPT-4."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""You are an expert advertising copywriter. Generate compelling ad copy for:
Product: {brief.get('product_name')}
Description: {brief.get('description')}
Target Audience: {brief.get('audience')}
Tone: {brief.get('tone')}

Return a JSON object with keys: headline, body, cta, tone, product_name, audience.
Keep headline under 10 words, body under 50 words, cta under 5 words."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        result["product_name"] = brief.get("product_name")
        result["audience"] = brief.get("audience")
        return result
    except Exception as e:
        print(f"OpenAI error: {e}, falling back to demo mode")
        brief_copy = dict(brief)
        return generate_copy({**brief_copy, "_force_demo": True})
