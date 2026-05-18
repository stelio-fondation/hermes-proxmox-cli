<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **hermes-proxmox-cli** (82 symbols, 88 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/hermes-proxmox-cli/context` | Codebase overview, check index freshness |
| `gitnexus://repo/hermes-proxmox-cli/clusters` | All functional areas |
| `gitnexus://repo/hermes-proxmox-cli/processes` | All execution flows |
| `gitnexus://repo/hermes-proxmox-cli/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

# Hermes Proxmox CLI

CLI de pilotage d'infrastructure Proxmox — compatible agents IA (Hermes, Claude Code, etc.).

## Project Location

- **Path**: `/root/hermes-proxmox-cli`
- **Stack**: Python 3.12+, Click, Proxmoxer
- **Repo**: GitHub (stelio-fondation)

## Commands

```bash
# Lancer l'outil
python -m proxmox_cli.main list
python -m proxmox_cli.main clone --source-id 100 --new-id 200 --name "vm-name" --node "pve1"

# Sync des dépendances
uv sync
```

## Architecture

```
proxmox_cli/
├── main.py          # Entry point Click
├── api.py           # Client Proxmox API (Proxmoxer)
├── commands/
│   ├── list.py      # Lister VMs/CTs
│   ├── clone.py     # Cloner templates
│   ├── config.py    # Config Cloud-Init
│   └── manage.py    # Start/stop/delete
```

## Key Files

| Fichier | Rôle |
|---------|------|
| `proxmox_cli/main.py` | Entry point CLI |
| `proxmox_cli/api.py` | Connexion à l'API Proxmox |
| `SKILL.md` | Instructions pour agents IA (workflow idempotent) |

## Conventions

- Python: `snake_case`
- CLI: Click commands
- Config: `.env` (PM_URL, PM_USER, PM_TOKEN, PM_VERIFY_SSL)
- Git: conventional commits (`feat/`, `fix/`, `chore/`, `docs/`)
