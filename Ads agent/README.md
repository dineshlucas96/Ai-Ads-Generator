# ⚡ AdGenius AI — Agentic Ads Platform

An AI-powered platform where **4 specialized agents** collaborate to generate advertising creatives from a simple product brief.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Set up API keys
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Run the app
python app.py

# 4. Open in browser
# http://localhost:5000
```

## 🤖 The 4 Agents

| Agent | Role |
|-------|------|
| ✍️ **Creative Agent** | Generates headlines, body copy, and CTAs |
| 🎨 **Design Agent** | Creates visual assets (DALL-E 3 or curated images) |
| 🔀 **Variation Agent** | Produces A/B test variations across 4 tones |
| 📱 **Platform Agent** | Adapts creatives for Instagram, Facebook, Twitter, LinkedIn, Google |

## 🔑 API Keys (Optional)

The app runs in **demo mode** by default with realistic mock data.

To use real AI generation, add to `.env`:
```
OPENAI_API_KEY=your_key_here
DEMO_MODE=false
```

## 📁 Project Structure

```
Ads agent/
├── app.py                  # Flask entry point
├── requirements.txt
├── .env.example
├── agents/
│   ├── creative_agent.py   # Copy generation
│   ├── design_agent.py     # Image generation
│   ├── variation_agent.py  # A/B variations
│   └── platform_agent.py   # Platform adaptation
├── routes/
│   └── api.py              # REST API endpoints
├── templates/
│   └── index.html          # Frontend SPA
└── static/
    ├── css/style.css
    └── js/app.js
```

## 🌐 API Endpoints

- `POST /api/generate` — Generate creatives from a brief
- `POST /api/refine` — Refine creatives via chat
- `GET /api/health` — Health check
