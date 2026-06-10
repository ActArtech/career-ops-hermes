# Career-Ops Hermes

<p align="center">
  <strong>AI-powered job search pipeline — now natively on Hermes Agent</strong>
</p>

Career-Ops turns Hermes Agent into a full job search command center. Instead of manually tracking applications in a spreadsheet, you get an AI-powered pipeline that:

- **Evaluates offers** with a structured A-F scoring system (10 weighted dimensions) + G (posting legitimacy check)
- **Generates tailored PDFs** — ATS-optimized CVs customized per job description
- **Scans portals** automatically (Greenhouse, Ashby, Lever, 45+ pre-configured companies)
- **Processes in batch** — evaluate 10+ offers in parallel with Hermes sub-agents
- **Tracks everything** in a single source of truth with integrity checks

> **Important: This is NOT a spray-and-pray tool.** Career-ops is a filter — it helps you find the few offers worth your time out of hundreds. Your time is valuable, and so is the recruiter's.

This project ports [santifer/career-ops](https://github.com/santifer/career-ops) v1.9.0 to run natively on **Hermes Agent**, leveraging Hermes built-in tools (browser, sub-agents, cron, memory) instead of external CLI dependencies.

## Quick Start

### Prerequisites

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed
- [Node.js](https://nodejs.org) (for scripts — scan, PDF generation, etc.)
- [Playwright](https://playwright.dev) for PDF generation: `npx playwright install chromium`

### Install

```bash
# Clone
git clone https://github.com/starMagic/career-ops-hermes.git
cd career-ops-hermes

# Install dependencies
npm install

# Install Hermes skills
./install.sh
```

### Usage

Open Hermes in the project directory:

```bash
cd career-ops-hermes
hermes
```

Then just start chatting:

- Paste a job URL or description → Hermes auto-evaluates it
- Say "scan for new offers" → scans configured portals
- Say "generate a CV for company X" → creates tailored PDF
- Say "show my tracker" → displays application status

## Hermes-Native Advantages

| Feature | career-ops (Claude Code) | career-ops-hermes |
|---------|--------------------------|-------------------|
| Browser automation | Requires Playwright MCP | Built-in (`browser_navigate`, `browser_snapshot`) |
| Batch workers | `claude -p` subprocess | `delegate_task` sub-agents |
| Recurring scanning | External cron | Built-in `cronjob` |
| Persistent memory | Files only | `memory` + files |
| Dashboard | Go TUI | Hermes WebUI |
| CLI dependency | Claude Code / Gemini / OpenCode | Hermes Agent only |

## Skills

17 skills ported from career-ops modes:

| Skill | What it does |
|-------|-------------|
| `career-ops-shared` | System context (load first) |
| `career-ops-evaluate` | A-G job evaluation |
| `career-ops-compare` | Multi-offer comparison |
| `career-ops-scan` | Portal scanner |
| `career-ops-pdf` | ATS-optimized CV (PDF) |
| `career-ops-latex` | LaTeX CV export |
| `career-ops-pipeline` | URL inbox processor |
| `career-ops-batch` | Mass batch processing |
| `career-ops-tracker` | Application tracker |
| `career-ops-apply` | Live form assistant |
| `career-ops-contact` | LinkedIn outreach |
| `career-ops-deep` | Company research |
| `career-ops-interview-prep` | Interview intelligence |
| `career-ops-training` | Course evaluation |
| `career-ops-project` | Portfolio evaluation |
| `career-ops-patterns` | Rejection pattern analysis |
| `career-ops-followup` | Follow-up cadence |

## Project Structure

```
career-ops-hermes/
├── AGENTS.md              # Hermes project context
├── README.md
├── install.sh             # Skill installation
├── skills/                # 17 Hermes skills (SKILL.md each)
├── scripts/               # Node.js utilities (zero changes from upstream)
├── templates/             # CV templates (HTML, LaTeX), portals config
├── providers/             # ATS providers (Greenhouse, Ashby, Lever...)
├── providers/             # ATS API parsers
├── fonts/                 # Space Grotesk + DM Sans
├── batch/                 # Batch processing scripts
├── dashboard/             # Go TUI (optional)
├── docs/                  # Documentation
├── writing-samples/       # Style calibration samples
└── data/                  # Runtime data (gitignored)
```

## License

MIT — same as upstream. Original copyright: Santiago Fernández de Valderrama.

Port and Hermes adaptation: same MIT license.

## Credits

- [santifer/career-ops](https://github.com/santifer/career-ops) — original project by [Santiago Fernández de Valderrama](https://santifer.io)
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — AI agent framework by Nous Research

---

**Upstream:** https://github.com/santifer/career-ops (v1.9.0)
