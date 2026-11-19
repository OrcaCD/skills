# Agents.md

This file provides guidance to AI Agents when working in this repository.

## What is this repository

User-facing [Agent Skills](https://agentskills.io) for [OrcaCD](https://orcacd.dev), a simple GitOps tool for Docker Compose. The skills are aimed at OrcaCD **users** working in their own GitOps repositories, not at contributors to OrcaCD itself. Contributor skills live in the [main repository](https://github.com/OrcaCD/orca-cd).

The repository root is a single plugin named `orcacd`, published through a marketplace of the same name for both Claude Code and Codex.

## Layout

```
.claude-plugin/
  plugin.json        # Claude Code plugin manifest
  marketplace.json   # Claude Code marketplace (plugin source: "./")
.codex-plugin/
  plugin.json        # Codex plugin manifest
.agents/plugins/
  marketplace.json   # Codex marketplace (plugin source: "./")
assets/
  icon.png           # plugin icon (square PNG, 512 px)
skills/
  <skill-name>/
    SKILL.md         # one directory per skill
    references/      # optional, loaded on demand
```

## Writing a skill

- Use the open `SKILL.md` format so skills work in Claude Code, Codex, Cursor and other agents. Don't rely on agent-specific frontmatter or tools.
- The directory name must match the `name` in the frontmatter (lowercase, hyphens).
- The `description` decides when an agent loads the skill. Say what the skill does and when to use it, with the words a user would actually type ("compose file", "deploy failed", …).
- Keep skills short and procedural. Link to the docs at `https://orcacd.dev/docs/...` instead of copying them; the full index is at https://orcacd.dev/llms.txt. OrcaCD changes a lot, and copied docs go stale with every breaking change.
- State the minimum supported version near the top of the body, e.g. `Requires OrcaCD ≥ 0.5.0.`
- Put long reference material in `references/` and link to it from `SKILL.md`, so it is only loaded when needed.

Example frontmatter:

```markdown
---
name: writing-compose-files
description: Write and review Docker Compose files and repository layouts for OrcaCD. Use when creating or changing a compose file in a repository deployed by OrcaCD.
---

Requires OrcaCD ≥ 0.5.0.
```

## Versioning and releases

- Plugin releases are tagged to match OrcaCD Hub versions (e.g. `v0.5.0`).
- The `version` field must be identical in `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. Bump both when releasing, otherwise installed plugins won't pick up the update.
- Keep the plugin name `orcacd` and the marketplace name `orcacd` stable; users install with `orcacd@orcacd`.

## Validation

Before opening a PR, check that the manifests are valid:

```sh
claude plugin validate .
```

When adding or renaming a skill, update the skills table in `README.md`.
