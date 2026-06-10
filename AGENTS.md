# Career-Ops Hermes — AI Job Search Pipeline

## Origin

This is a **Hermes-native port** of [santifer/career-ops](https://github.com/santifer/career-ops) v1.9.0 — an AI-powered job search automation system that evaluates offers, generates tailored CVs, scans portals, and tracks applications. The original author used it to evaluate 740+ job offers, generate 100+ tailored CVs, and land a Head of Applied AI role.

Original copyright: Santiago Fernández de Valderrama, MIT License.

This port adapts career-ops to run natively on **Hermes Agent**, replacing external CLI dependencies (Claude Code, Playwright MCP, etc.) with Hermes built-in tools.

## Data Contract (CRITICAL)

**User Layer (NEVER auto-updated, personalization goes HERE):**
- `cv.md`, `config/profile.yml`, `modes/_profile.md`, `article-digest.md`, `portals.yml`
- `data/*`, `reports/*`, `output/*`, `interview-prep/*`

**System Layer (auto-updatable):**
- `skills/*.md`, `AGENTS.md`, `*.mjs` scripts, `dashboard/*`, `templates/*`, `batch/*`

**THE RULE: When the user asks to customize anything, ALWAYS write to `modes/_profile.md` or `config/profile.yml`. NEVER edit system-layer files for user-specific content.**

## Skill Modes

| User wants to... | Load skill |
|-----------------|------------|
| Evaluate a job offer | `career-ops-evaluate` |
| Compare multiple offers | `career-ops-compare` |
| Generate ATS-optimized CV (PDF) | `career-ops-pdf` |
| Export CV as LaTeX | `career-ops-latex` |
| Scan portals for new offers | `career-ops-scan` |
| Process pending URLs | `career-ops-pipeline` |
| Batch process offers | `career-ops-batch` |
| View/update application tracker | `career-ops-tracker` |
| Fill application forms | `career-ops-apply` |
| LinkedIn outreach message | `career-ops-contact` |
| Deep company research | `career-ops-deep` |
| Interview preparation | `career-ops-interview-prep` |
| Evaluate course/cert | `career-ops-training` |
| Evaluate portfolio project | `career-ops-project` |
| Analyze rejection patterns | `career-ops-patterns` |
| Follow-up cadence tracker | `career-ops-followup` |

**Always load `career-ops-shared` first** — it contains archetypes, scoring, writing style, and ethical rules that all other skills depend on.

## Skill Loading Pattern

When the user pastes a JD or URL:
```
skill_view(name="career-ops-shared")
skill_view(name="career-ops-evaluate")
```

Then execute the evaluation flow described in the skill.

## Hermes-Native Tool Mapping

| career-ops original | Hermes equivalent |
|--------------------|--------------------|
| Playwright (browser_navigate, browser_snapshot) | `browser_navigate`, `browser_snapshot`, `browser_click` |
| WebSearch | `web_search` |
| WebFetch | `web_extract` |
| Bash | `terminal` |
| Read | `read_file` |
| Write | `write_file` |
| Edit | `patch` |
| `claude -p` (headless workers) | `delegate_task` |
| /slash commands | Skill names (load with `skill_view`) |
| Canva MCP | Optional MCP (if configured) |
| Recurring scan | `cronjob` |

## Scripts (zero changes)

All Node.js scripts from career-ops run as-is via `terminal`:
- `node scan.mjs` — portal scanner
- `node generate-pdf.mjs` — HTML to PDF
- `node generate-latex.mjs` — LaTeX compilation
- `node merge-tracker.mjs` — merge tracker additions
- `node verify-pipeline.mjs` — pipeline health check
- `node normalize-statuses.mjs` — status normalization
- `node dedup-tracker.mjs` — deduplication
- `node analyze-patterns.mjs` — pattern analysis
- `node followup-cadence.mjs` — follow-up cadence
- `node cv-sync-check.mjs` — CV sync check

## Ethical Use — CRITICAL

- **NEVER submit an application without the user reviewing it first.**
- **Strongly discourage low-fit applications** (score < 4.0/5).
- **Quality over speed** — a well-targeted application to 5 companies beats 50 generic blasts.

## CV Source of Truth

- `cv.md` in project root is the canonical CV
- `article-digest.md` has detailed proof points (optional)
- **NEVER hardcode metrics** — read from these files at evaluation time

## Stack

- Node.js (mjs modules), HTML/CSS (CV template), YAML (config), Markdown (data)
- Scripts: `scripts/*.mjs`
- Output: `output/` (gitignored), Reports: `reports/` (gitignored)
- Hermes native: browser tools, sub-agents, cron, memory
