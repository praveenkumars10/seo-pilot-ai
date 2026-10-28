# SEO Pilot AI — Architecture & Technical Specifications

## 1. Executive Overview
SEO Pilot AI is an autonomous SEO engineering platform designed to run locally in development and scale to production. It combines:
- Real live HTTP web crawling.
- Local repository AST & static code analysis.
- Multi-provider AI model orchestration (Gemini, Claude, OpenAI, Meta/Ollama).
- Google Search Console API and Google Analytics Data API integrations.
- A **Consolidated Approval Workflow Gatekeeper** ensuring no code is modified without explicit human confirmation.
- Automated post-modification regression testing with automatic rollback.
- Credential-safe Git commit and push automation.

```
+-----------------------------------------------------------------------------------+
|                                  React 19 Frontend                                |
|  - Dashboard Overview    - Audit Engine         - Consolidated Approval Gatekeeper|
|  - Website Registry      - Google Integrations  - Multi-Provider AI Management    |
+-----------------------------------------------------------------------------------+
                                          | HTTP (REST)
                                          v
+-----------------------------------------------------------------------------------+
|                                FastAPI Backend                                    |
|  - Async SQLAlchemy 2.0  - Unified Schemas      - Background Task Worker          |
+-----------------------------------------------------------------------------------+
         |                        |                         |
         v                        v                         v
+------------------+    +--------------------+    +----------------------------------+
|  Crawler Engine  |    |  Multi-Model AI    |    |   Approval & Code Modifier       |
| - Status codes   |    | - Google Gemini    |    | - Single Confirmation Gatekeeper |
| - Titles & Metas |    | - Anthropic Claude |    | - Pre-Apply Snapshots / Backup   |
| - Alt attributes |    | - OpenAI ChatGPT   |    | - Automated Verification Tests   |
| - Robots & Schema|    | - Meta AI (Local)  |    | - Auto Rollback on Failure       |
| - Code AST scan  |    | - Deterministic    |    | - Clean Git Commits & Push       |
+------------------+    +--------------------+    +----------------------------------+
```

---

## 2. Core Subsystems

### A. Live Crawler & Code Analyzer
- **`SEOCrawlerService`**: Traverses live website URLs within the canonical domain up to configurable page limits. Analyzes HTTP status codes, title length, meta description length, canonical links, robots meta (noindex/nofollow), heading structure (H1-H6 hierarchy), image alt attributes, OpenGraph tags, and Schema.org JSON-LD syntax.
- **`LocalCodeAnalyzerService`**: Scans the actual repository source code (HTML, JSX, TSX, Astro, Vue). Locates exact files and line numbers where meta tags, alt attributes, or assets are missing.

### B. Multi-Provider AI Orchestration
- **`AIOrchestrator`**:
  - Priority: Gemini (Primary) -> Claude -> OpenAI -> Meta -> Deterministic Rule Engine.
  - Automatic quota fallback: If an external model exceeds quota or rate limit, requests seamlessly cascade.
  - Offline Safety: When no API keys are present, the internal **Deterministic Rule Engine** synthesizes exact valid diffs so development is never blocked.
  - Consensus & Peer Review: Secondary models independently audit diffs for syntax regressions before presentation to the user.

### C. Consolidated Approval Gatekeeper
- Consolidates all proposed file modifications into a single review batch.
- Displays side-by-side unified diffs, list of affected files, and automated tests to run.
- Zero silent edits: Files are only touched upon explicit human approval.
- Automatic snapshot: Target files are backed up to `.seopilot_backups/` before any write.
- Automated Test Runner: Executes build/test commands (e.g. `npm run build`, `pytest`).
- Automatic Rollback: If tests fail, files are restored to their pristine state immediately.

### D. Git & GitHub Integration
- Safe staging: Barred from staging `.env`, keys, tokens, or credential files.
- Meaningful commit messages: Links commits to resolved issue IDs.
- Remote push: Only executes when explicitly checked and authorized by the user.

### E. Google OAuth2 Integrations
- Search Console API: List sites, query search performance (clicks, impressions, CTR, position), and inspect individual URLs.
- Google Analytics 4: Reports organic search sessions, channels, and landing page metrics.
