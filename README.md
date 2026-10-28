# SEO Pilot AI — Autonomous SEO Engineering Platform

> **Production-Oriented Autonomous SEO Engine, Code Analyzer, Multi-Model AI Orchestrator & Consolidated Approval System**

---

## 🌟 Highlights

1. **Autonomous Live Crawler & Code Analyzer**:
   - Inspects live HTTP response codes, redirects, canonicals, robots directives, image alt attributes, and Schema.org JSON-LD.
   - Deep scans local codebases (HTML, React, Next.js, Astro) with exact file and line number pinpointing.
2. **Consolidated Approval Gatekeeper**:
   - One consolidated human approval review for entire batches of changes.
   - Interactive unified diff viewer for every affected file.
   - Pre-change automatic snapshots and instant automated rollback if verification tests fail.
3. **Multi-Model AI Orchestrator**:
   - Connects to **Google Gemini**, **Anthropic Claude**, **OpenAI ChatGPT**, and **Meta / Local Models (Ollama)**.
   - Built-in fallback to an offline **Deterministic SEO Engine** if no external API keys are configured.
4. **Google Search Console & Google Analytics 4**:
   - Official OAuth 2.0 integration for real search clicks, impressions, CTR, positions, and organic session data.
5. **Git & GitHub Version Control**:
   - Safe automated commits and authorized pushes with strict secret redaction (`.env`, tokens are barred).

---

## 🚀 Quick Start (Windows)

### Prerequisites
- Python 3.11+
- Node.js v18+ & npm

### Launching the Application
Simply double click `start.bat` or run:

```bash
# Terminal 1: Backend
.\backend\venv\Scripts\python .\backend\run.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

- **Web Dashboard**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚙️ Configuration (`.env`)

Copy `.env.example` to `.env`:

```env
# Google OAuth 2.0 (Search Console & Analytics)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/google/oauth2callback

# AI Model Keys (Optional - System falls back automatically)
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
META_AI_BASE_URL=http://localhost:11434/v1
```

---

## 🧪 Automated Testing

Run the comprehensive pytest suite:

```bash
.\backend\venv\Scripts\pytest .\backend\tests -v
```

Build the frontend for production:

```bash
cd frontend && npm run build
```

