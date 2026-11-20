# <div align="center"><img alt="OrcaCD logo" src="https://raw.githubusercontent.com/OrcaCD/orca-cd/f6fb48965df90a57a2b181e9e2b359653ae5c6b9/frontend/public/assets/logo-dark-256.png" width="100"/> <br>OrcaCD Skills</div>

<div align="center">
Agent skills and plugins for <a href="https://orcacd.dev">OrcaCD</a><br><br>

<a href="https://github.com/OrcaCD/skills/blob/main/LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/github/OrcaCD/skills/license.svg?logo=opensourceinitiative&logoColor=%233da639&mode=dark&size=sm&variant=outline"><img alt="License" src="https://shieldcn.dev/github/OrcaCD/skills/license.svg?logo=opensourceinitiative&logoColor=%233da639&mode=light&size=sm&variant=outline"></picture></a>
<a href="https://github.com/OrcaCD/skills/issues"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/github/OrcaCD/skills/issues.svg?logo=github&mode=dark&size=sm&variant=outline"><img alt="GitHub Issues" src="https://shieldcn.dev/github/OrcaCD/skills/issues.svg?logo=github&logoColor=%23181717&mode=light&size=sm&variant=outline"></picture></a>
</div>

This repository teaches AI coding agents how to work with OrcaCD. It contains [Agent Skills](https://agentskills.io) (`SKILL.md`) that cover how OrcaCD expects a repository and its compose files to look, and what to do when a deploy fails. The skills are packaged as a plugin for Claude Code and Codex, and the `SKILL.md` files also work in any other agent that supports the format.

The plugin also connects your agent to the MCP server of your OrcaCD Hub, so it can read the status and errors of your applications and deploy them after showing you a preview.

> [!WARNING]
> OrcaCD is in early development and not yet production-ready. Expect breaking changes. The skills always target the latest OrcaCD release.

## Installation

### Claude Code

```sh
/plugin marketplace add OrcaCD/skills
/plugin install orcacd@orcacd
```

Claude Code asks for the URL of your Hub, e.g. `https://orcacd.example.com`. Leave it empty to only use the skills, or set it later with `/plugin configure orcacd@orcacd`. Then run `/mcp` and authenticate the `orcacd` server: OrcaCD opens in the browser, where you log in and choose what the agent may do.

### Codex

```sh
codex plugin marketplace add OrcaCD/skills
codex plugin add orcacd@orcacd
```

Codex plugins can't ask for the Hub URL, so add the MCP server yourself. Codex opens OrcaCD in the browser to log in:

```sh
codex mcp add orcacd --url https://orcacd.example.com/api/v1/mcp
```

### Other agents (Cursor, OpenCode, Gemini CLI, …)

```sh
npx skills add OrcaCD/skills
```

To use the MCP server, add `https://<your-hub>/api/v1/mcp` as a remote (streamable HTTP) MCP server in your agent.

## Skills

| Skill | Description | Requires |
| ----- | ----------- | -------- |
| [writing-compose-files](skills/writing-compose-files/SKILL.md) | Repository layout and compose files that pass the agent's checks | OrcaCD ≥ 0.6.0 |
| [fixing-failed-deploys](skills/fixing-failed-deploys/SKILL.md) | From a failed or unhealthy application to the cause and the fix, using the MCP server when connected | OrcaCD ≥ 0.6.0 |
| [setting-up-orcacd](skills/setting-up-orcacd/SKILL.md) | Install the Hub and an agent, connect a repository and the MCP server | OrcaCD ≥ 0.6.0 |
| [migrating-to-orcacd](skills/migrating-to-orcacd/SKILL.md) | Move manual `docker compose` stacks, Portainer stacks and Watchtower to OrcaCD without losing data | OrcaCD ≥ 0.6.0 |

## MCP server

The Hub serves an MCP server at `/api/v1/mcp` with these tools:

| Tool | Scope |
| ---- | ----- |
| `list_applications`, `get_application` | `application:read` |
| `list_agents` | `agent:read` |
| `preview_deploy`, `deploy_application` | `application:deploy` |

You choose the scopes when you log in. A deploy always needs a preview first, so the agent can't deploy something you haven't seen. Connections show up under **Settings → API Tokens** in OrcaCD, where you can revoke them. Set `DISABLE_MCP=true` on the Hub to turn the MCP server off.

## Privacy

The plugin only connects to the OrcaCD Hub you configure. No data is sent to the OrcaCD project or anyone else.

## Versioning

There are no plugin releases: `main` is the latest version, and every commit is an update. To get the latest skills, run `/plugin marketplace update orcacd` in Claude Code or `codex plugin marketplace upgrade orcacd` in Codex.

Each skill states the minimum OrcaCD version it supports. If you run an older Hub, you can pin the skills to the tag of your Hub version, e.g. `codex plugin marketplace add OrcaCD/skills@v0.5.0`.

## Contribute

Contributions are very welcome! See [AGENTS.md](AGENTS.md) for the repository layout and how to write a skill. For changes to OrcaCD itself, head over to the [main repository](https://github.com/OrcaCD/orca-cd). For the documentation, see the [docs repository](https://github.com/OrcaCD/docs).

## License

[MIT](LICENSE)
