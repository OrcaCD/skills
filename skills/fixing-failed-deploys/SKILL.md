---
name: fixing-failed-deploys
description: Diagnose and fix failed or unhealthy OrcaCD deployments. Use when an OrcaCD application is out of sync, a deploy or sync failed, an application was rolled back, is stuck syncing, or is unhealthy, degraded or stopped after a deploy.
---

# Fixing failed OrcaCD deploys

Requires OrcaCD ≥ 0.6.0.

Work through these steps in order: find out what failed, map the error to a cause, fix it in Git, and redeploy.

## 1. Get the state

**With the OrcaCD MCP server connected** (tools like `list_applications` and `get_application`):

1. Call `list_applications` to find the application, its `syncStatus`, `healthStatus` and `lastSyncError`.
2. Call `get_application` with its `id`. It returns the compose file, the compose warnings, the last sync error and the recent events with their errors.
3. If the problem might be the agent, call `list_agents` and check its `status`.

**Without MCP**, ask the user to open the application in OrcaCD and send you:

- The red **Sync failed** alert and the **Compose configuration warnings** on the **Details** page.
- The failed entries on the **History** page, with their error. Image update failures only show up there.
- The status of the agent on the **Agents** page.

If the MCP server should be available but isn't, see the `setting-up-orcacd` skill for how to connect it.

## 2. Find the cause

| What you see | Likely cause |
| --- | --- |
| `deployment rejected by security policy: ...` | The compose file breaks the deployment policy. Fix it as described in the `writing-compose-files` skill. |
| `unsupported Compose feature "include"` (or `extends`, `label_file`) | The file references other files, which don't exist on the agent. |
| `load compose project: ...` | Invalid YAML or compose schema. |
| `compose project "x" already exists and is not managed by OrcaCD` | Containers from a project with the same name, started outside OrcaCD, are still running on the host. Stop them (`docker compose -p x down`, keeps volumes) or rename the application. |
| `agent is offline`, `could not connect to agent`, `agent disconnected before the deployment result was received` | The agent was offline. Get it back online, then redeploy. Deployments are not retried automatically. |
| `docker daemon is not ready`, agent status `error` | The agent can't reach Docker on its host. |
| `no credentials for <registry> found in the agent's Docker config` | Private image without registry credentials. Run `docker login <registry>` on the agent host, as the user that starts the agent, and recreate the agent. |
| `compose up: ...` with `port is already allocated`, `Conflict. The container name ... is already in use`, `pull access denied`, `manifest unknown` | A normal Docker error: port or container name in use, or a wrong image name or tag. |
| `commit <sha> failed signature verification` | The repository requires signed commits and the commit isn't signed by a trusted key. |
| `health check failed: ...`, application **Rolled back** | The deploy worked, but the application didn't become healthy, so OrcaCD rolled it back. See step 4. |
| Image update failed in **History** only | Image polling or the image webhook couldn't pull. Usually registry credentials or a removed tag. |
| Stuck in **Syncing** | Check that the agent is online and look at the agent logs. |

More messages and their fixes are in [references/error-messages.md](references/error-messages.md).

## 3. Fix it in Git

OrcaCD deploys what is committed. Fix the compose file in the repository, never in the deployment directory on the agent: OrcaCD overwrites it on the next deploy.

After the commit is pushed, OrcaCD deploys it automatically with polling or a webhook. With manual sync, or to deploy right away, the user clicks **Sync repository** in the dropdown next to **Deploy**.

Some causes aren't in the compose file: agent offline, registry credentials, env values (set under **Settings → Environment Variables**). Fix those, then redeploy without a new commit (step 5).

## 4. Rolled back or unhealthy

- **Rolled back**: the application runs an earlier deployment and is `Out of Sync` on purpose. With the default settings, auto-sync is paused, so new commits don't deploy until the user clicks **Retry deploy** or **Resume auto-sync** on the details page. `get_application` shows this as `rolledBackCommit` and `autoSyncPaused`.
- **Unhealthy, degraded or stopped**: look at the logs of the containers on the agent host: `docker compose -p <project> logs --tail 100`. The project name is the application name in lowercase, with characters other than `a-z`, `0-9` and `_` replaced by `-`.
- Containers that exit after their work (migrations, init jobs) count as unhealthy. They make every deploy fail a health check.

## 5. Redeploy

**With MCP** (needs the `application:deploy` scope):

1. Call `preview_deploy` with the application's `id`.
2. Show the user the diff and every warning, e.g. an offline agent.
3. Only after the user agrees, call `deploy_application` with the `previewId`.
4. The deploy runs in the background. Call `get_application` after a few seconds to check the result.

`deploy_application` deploys the commit OrcaCD already has, like the **Deploy** button. It doesn't fetch new commits from Git. If the fix is a new commit, wait for the repository sync, or ask the user to click **Sync repository**.

**Without MCP**, the user clicks **Deploy** on the application's details page.

## Don't

- Don't suggest adding the application to `ALLOWED_PRIVILEGED_APPS` to get past a policy error. It turns off all security checks. Fix the compose file instead, and only mention the option if the application really needs host access.
- Don't run `docker compose up` in the deployment directory to fix things by hand. OrcaCD won't know about it.
- Don't deploy without showing the user the preview first.
