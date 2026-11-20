---
name: setting-up-orcacd
description: Install and configure OrcaCD, the GitOps tool for Docker Compose. Use when installing the OrcaCD Hub or an agent, connecting a Git repository, choosing between webhooks and polling, creating the first application, or connecting an AI agent to the OrcaCD MCP server.
---

# Setting up OrcaCD

Requires OrcaCD ≥ 0.6.0.

OrcaCD has two parts: the **Hub** (web UI, API, state) and an **Agent** on every Docker host that deploys the applications. Both can run on the same machine. Walk the user through these steps and link to the docs for details. Don't invent settings: the docs at <https://orcacd.dev/llms.txt> list every page.

## 1. Install the Hub and an agent

Follow [Installation](https://orcacd.dev/docs/setup/installation):

1. Download `docker-compose.yml`, `.env` (Hub) and `agent.env` (agent) from the OrcaCD repository.
2. In `.env`, set `APP_URL` to the public URL of the Hub and `APP_SECRET` to the output of `openssl rand -base64 42`.
3. Keep the Hub and the agent in separate env files. Never give the agent `APP_SECRET`: deployed compose files can read the agent's environment.
4. Pin the image tags in `docker-compose.yml` instead of `latest`.
5. `docker compose up -d`.

The Hub listens on `127.0.0.1:8080`. Put a reverse proxy with TLS in front of it ([guide](https://orcacd.dev/docs/guides/reverse-proxy)), and set `TRUSTED_PROXIES`. For a local test, use `APP_URL=http://localhost:8080` and `HUB_URL=http://hub:8080` instead.

## 2. Create the admin account

Get the one-time setup code with `docker compose logs hub | grep setup-code` and open the link from the log line.

## 3. Connect the agent

In the UI, go to **Agents → Add Agent**. For the agent from step 1, copy only the token (**Copy agent auth token**) into `AUTH_TOKEN` in `agent.env`, then run `docker compose up -d agent`. A plain restart doesn't reload the env file.

For another host, copy the generated `compose.yml` from the setup dialog to that host and run `docker compose up -d` there. See [Agents](https://orcacd.dev/docs/advanced/architecture/agents).

## 4. Add a repository

Go to **Repositories → Add Repository**. Supported: GitHub, GitLab, Gitea and Azure DevOps. Private repositories need a read-only token (GitHub: fine-grained token with **Contents: read**, GitLab: `read_repository`).

Choose the sync strategy:

| Strategy | Use when |
| --- | --- |
| Webhook | The Hub is reachable from the Git provider. Deploys right after a push. Set up the webhook as described in [Webhooks](https://orcacd.dev/docs/configuration/webhooks#git-providers). |
| Polling | The Hub isn't reachable from the internet. Checks every 60 seconds by default. |
| Manual | Deploys only when someone clicks **Sync**. |
| GitHub Actions | Deploy at the end of a CI workflow, without stored secrets. Enable **GitHub Actions Access** on the repository and use `OrcaCD/deploy-action` ([guide](https://orcacd.dev/docs/guides/github-actions)). |

Recommend enabling **Require signed commits** in the repository's **Signing** settings if the team signs commits.

## 5. Create an application

Go to **Applications → New Application** and pick the agent, repository, branch and compose file. OrcaCD deploys it right away. For writing the compose file, use the `writing-compose-files` skill.

Afterwards, in the application's settings:

- **Environment Variables**: set the values of the env files the compose file references.
- **Image Updates**: enable image polling or the image pull webhook if the application uses mutable tags like `latest`.
- **Rollbacks**: optionally roll back failed deployments automatically.

## 6. Connect your AI agent to OrcaCD

The Hub has an MCP server at `https://<hub>/api/v1/mcp`. It lets an AI agent list applications and agents, read deploy errors and deploy after showing a preview. It's on by default; `DISABLE_MCP=true` on the Hub turns it off.

- **Claude Code with the OrcaCD plugin**: run `/plugin configure orcacd@orcacd`, enter the Hub URL, then run `/mcp` and authenticate the `orcacd` server.
- **Codex**: `codex mcp add orcacd --url https://<hub>/api/v1/mcp`. It opens the login in the browser. Later, `codex mcp login orcacd` logs in again.
- **Other clients**: add `https://<hub>/api/v1/mcp` as a remote (streamable HTTP) MCP server.

The client opens OrcaCD in the browser, the user logs in and picks the permissions:

| Scope | Allows |
| --- | --- |
| `application:read` | List applications, read their compose file, status and errors |
| `agent:read` | List agents and their status |
| `application:deploy` | Preview and deploy applications |

The connection shows up under **Settings → API Tokens**, where the user can revoke it. Clients without OAuth can send an API token from that page as `Authorization: Bearer <token>` instead.

## 7. Harden

Point the user to the [security checklist](https://orcacd.dev/docs/advanced/security). The most important items are OIDC with MFA, `TRUSTED_PROXIES`, signed commits and `RESTRICT_VOLUMES_TO_DEPLOYMENTS_DIR=true` on agents.
