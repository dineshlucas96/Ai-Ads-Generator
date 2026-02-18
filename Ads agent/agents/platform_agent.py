def adapt_for_platforms(brief: dict, copy: dict, images: list, platforms: list) -> dict:
    """
    Platform Agent: Adapts creatives to platform-specific formats and specs.
    Returns a dict keyed by platform name with adapted specs and copy.
    """
    all_platforms = {
        "instagram": {
            "name": "Instagram",
            "icon": "📸",
            "color": "#E1306C",
            "formats": [
                {"name": "Feed Post", "ratio": "1:1", "width": 1080, "height": 1080, "css_ratio": "1/1"},
                {"name": "Story", "ratio": "9:16", "width": 1080, "height": 1920, "css_ratio": "9/16"},
                {"name": "Reel Cover", "ratio": "9:16", "width": 1080, "height": 1920, "css_ratio": "9/16"},
            ],
            "copy_limits": {"headline": 40, "body": 125, "cta": 20},
            "tips": "Use bold visuals, minimal text. Stories perform best with motion.",
            "audience_reach": "2B+ users",
            "best_for": "Visual brands, lifestyle, fashion, food"
        },
        "facebook": {
            "name": "Facebook",
            "icon": "👥",
            "color": "#1877F2",
            "formats": [
                {"name": "Feed Ad", "ratio": "1.91:1", "width": 1200, "height": 628, "css_ratio": "1.91/1"},
                {"name": "Square Post", "ratio": "1:1", "width": 1080, "height": 1080, "css_ratio": "1/1"},
                {"name": "Story", "ratio": "9:16", "width": 1080, "height": 1920, "css_ratio": "9/16"},
            ],
            "copy_limits": {"headline": 40, "body": 125, "cta": 20},
            "tips": "Longer copy works well. Include social proof and clear value proposition.",
            "audience_reach": "3B+ users",
            "best_for": "All demographics, retargeting, lead generation"
        },
        "twitter": {
            "name": "Twitter / X",
            "icon": "🐦",
            "color": "#000000",
            "formats": [
                {"name": "Promoted Tweet", "ratio": "16:9", "width": 1200, "height": 675, "css_ratio": "16/9"},
                {"name": "Card Image", "ratio": "2:1", "width": 800, "height": 400, "css_ratio": "2/1"},
            ],
            "copy_limits": {"headline": 70, "body": 280, "cta": 20},
            "tips": "Be concise and punchy. Use trending hashtags. Engage with replies.",
            "audience_reach": "550M+ users",
            "best_for": "Tech, news, real-time marketing, B2B"
        },
        "linkedin": {
            "name": "LinkedIn",
            "icon": "💼",
            "color": "#0A66C2",
            "formats": [
                {"name": "Sponsored Content", "ratio": "1.91:1", "width": 1200, "height": 627, "css_ratio": "1.91/1"},
                {"name": "Square Ad", "ratio": "1:1", "width": 1080, "height": 1080, "css_ratio": "1/1"},
            ],
            "copy_limits": {"headline": 70, "body": 150, "cta": 20},
            "tips": "Professional tone works best. Lead with value, include industry insights.",
            "audience_reach": "900M+ professionals",
            "best_for": "B2B, recruiting, professional services, SaaS"
        },
        "google": {
            "name": "Google Display",
            "icon": "🔍",
            "color": "#4285F4",
            "formats": [
                {"name": "Leaderboard", "ratio": "728:90", "width": 728, "height": 90, "css_ratio": "728/90"},
                {"name": "Medium Rectangle", "ratio": "300:250", "width": 300, "height": 250, "css_ratio": "300/250"},
                {"name": "Large Rectangle", "ratio": "336:280", "width": 336, "height": 280, "css_ratio": "336/280"},
            ],
            "copy_limits": {"headline": 30, "body": 90, "cta": 15},
            "tips": "Keep it simple. Strong CTA. Test multiple sizes for best reach.",
            "audience_reach": "90% of internet users",
            "best_for": "Retargeting, brand awareness, search intent"
        }
    }

    result = {}
    selected = platforms if platforms else list(all_platforms.keys())

    for platform_key in selected:
        if platform_key not in all_platforms:
            continue

        platform = all_platforms[platform_key]
        limits = platform["copy_limits"]

        # Truncate copy to platform limits
        adapted_headline = copy.get("headline", "")[:limits["headline"]]
        adapted_body = copy.get("body", "")[:limits["body"]]
        adapted_cta = copy.get("cta", "")[:limits["cta"]]

        result[platform_key] = {
            **platform,
            "adapted_copy": {
                "headline": adapted_headline,
                "body": adapted_body,
                "cta": adapted_cta
            },
            "primary_image": images[0]["url"] if images else None,
            "primary_format": platform["formats"][0]
        }

    return result
