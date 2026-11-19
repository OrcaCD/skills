# <div align="center"><img src="https://raw.githubusercontent.com/OrcaCD/orca-cd/f6fb48965df90a57a2b181e9e2b359653ae5c6b9/frontend/public/assets/logo-dark-256.png" width="100"/> <br>OrcaCD Skills</div>

<div align="center">
Agent skills and plugins for <a href="https://orcacd.dev">OrcaCD</a><br><br>

<a href="https://github.com/OrcaCD/skills/blob/main/LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/github/OrcaCD/skills/license.svg?logo=opensourceinitiative&logoColor=%233da639&mode=dark&size=sm&variant=outline"><img alt="License" src="https://shieldcn.dev/github/OrcaCD/skills/license.svg?logo=opensourceinitiative&logoColor=%233da639&mode=light&size=sm&variant=outline"></picture></a>
<a href="https://github.com/OrcaCD/skills/issues"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/github/OrcaCD/skills/issues.svg?logo=github&mode=dark&size=sm&variant=outline"><img alt="GitHub Issues" src="https://shieldcn.dev/github/OrcaCD/skills/issues.svg?logo=github&logoColor=%23181717&mode=light&size=sm&variant=outline"></picture></a>
</div>

This repository teaches AI coding agents how to work with OrcaCD. It contains [Agent Skills](https://agentskills.io) (`SKILL.md`) that cover how OrcaCD expects a repository and its compose files to look, and what to do when a deploy fails. The skills are packaged as a plugin for Claude Code and Codex, and the `SKILL.md` files also work in any other agent that supports the format.

> [!WARNING]
> OrcaCD is in early development and not yet production-ready. Expect breaking changes. The skills always target the latest OrcaCD release.

## Installation

### Claude Code

```sh
/plugin marketplace add OrcaCD/skills
/plugin install orcacd@orcacd
```

### Codex

```sh
codex plugin marketplace add OrcaCD/skills
codex plugin add orcacd@orcacd
```

### Other agents (Cursor, OpenCode, Gemini CLI, …)

```sh
npx skills add OrcaCD/skills
```

## Skills

| Skill | Description | Requires |
| ----- | ----------- | -------- |
| _coming soon_ | | |

Planned skills (see [OrcaCD/orca-cd#536](https://github.com/OrcaCD/orca-cd/issues/536)):

- **Writing compose files:** repository layout and compose files that pass the agent's checks.
- **Fixing a failed deploy:** from a failed state to the likely cause and the fix.
- **Setup and onboarding:** install the Hub and an agent, connect a repository, webhooks vs. polling.
- **Migrating to OrcaCD:** from manual `docker compose`, Portainer stacks or Watchtower.

An MCP server built into the Hub will give agents access to live application and deploy status. Once it ships, this plugin will also configure it.

## Versioning

There are no plugin releases: `main` is the latest version, and every commit is an update. To get the latest skills, run `/plugin marketplace update orcacd` in Claude Code or `codex plugin marketplace upgrade orcacd` in Codex.

Each skill states the minimum OrcaCD version it supports. If you run an older Hub, you can pin the skills to the tag of your Hub version, e.g. `codex plugin marketplace add OrcaCD/skills@v0.5.0`.

## Contribute

Contributions are very welcome! See [AGENTS.md](AGENTS.md) for the repository layout and how to write a skill. For changes to OrcaCD itself, head over to the [main repository](https://github.com/OrcaCD/orca-cd). For the documentation, see the [docs repository](https://github.com/OrcaCD/docs).

## License

[MIT](LICENSE)
