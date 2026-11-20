# OrcaCD error messages

Errors appear in the **Sync failed** alert on the application's details page, on the **History** page and in `lastSyncError` and `recentEvents[].error` from the MCP tools.

## Compose file

| Message | Fix |
| --- | --- |
| `deployment rejected by security policy: ...` | Remove or change the rejected setting. The rest of the message lists every violation. See the `writing-compose-files` skill. |
| `unsupported Compose feature "<feature>" ...: local Compose references are not resolved` | Inline the referenced file. Only the compose file itself reaches the agent. |
| `load compose project: ...` | Fix the YAML or compose schema. Check with `docker compose -f <file> config --quiet`. |
| `compose file is empty` | The file at the application's path is empty on that branch. |
| `... could not be checked for symlinks: ... permission denied` | A container made a directory the agent can't read. See [Common Issues](https://orcacd.dev/docs/troubleshooting/common-issues#deployment-fails-with-permission-denied-during-symlink-checks). |

## Repository and sync

| Message | Fix |
| --- | --- |
| `commit <sha> failed signature verification: commit is not signed` / `not signed by a trusted key` | Sign the commit with a key that is trusted in the repository's **Signing** settings, or add the key there. |
| `signed commits are required but no trusted signing keys are configured` | Add a trusted key in the repository's **Signing** settings. |
| Repository status `Failed` with an authentication error | The auth token expired, was revoked or lacks read access to the contents. Update it in the repository's **Auth** settings. |
| Pushes don't trigger a sync | Check the webhook URL, secret and push events in the Git provider, see [Webhooks](https://orcacd.dev/docs/configuration/webhooks). |

## Agent

| Message | Fix |
| --- | --- |
| `agent is offline; cannot deploy application`, `could not connect to agent: <name>` | Start the agent and check its logs, then redeploy. See [Agent stays Offline](https://orcacd.dev/docs/troubleshooting/common-issues#agent-stays-offline-after-connecting). |
| `agent disconnected before the deployment result was received` | The agent lost its connection during the deploy. Redeploy once it's back. |
| `docker daemon is not ready` | The agent can't reach Docker. Check that Docker runs and that the agent has `use_api_socket: true` in its own compose file. |
| `compose project "<name>" already exists and is not managed by OrcaCD` | Stop the containers that were started outside OrcaCD, or rename the application. |

## Images

| Message | Fix |
| --- | --- |
| `no credentials for <registry> found in the agent's Docker config` | Run `docker login <registry>` on the agent host as the user that starts the agent, then `docker compose up -d agent`. |
| `pull access denied`, `manifest unknown`, `not found` | Wrong image name or tag, or the tag was deleted. |
| `application is rolled back; deploy it again before pulling images` | Image updates are paused while rolled back. Retry the deploy or resume auto-sync first. |

## Health and rollbacks

| Message | Fix |
| --- | --- |
| `health check failed: application was <health> for <n>s after the deployment` | Containers crashed or failed their healthcheck right after the deploy. Check the container logs. |
| `health check failed: ... did not become healthy within <n>s` | Containers were still starting or unhealthy when the time ran out. Fix the healthcheck, or raise the timeout under **Settings → Rollbacks**. |
| `health check failed: the agent did not report the application's health` | The agent went offline during the health check. |
| `rollback failed: ...` | The rollback failed too and isn't retried. Fix the cause and deploy again. |

## Env files

| Message | Fix |
| --- | --- |
| `the changes were saved, but redeploying the application failed: ...` | The new values were written, but the deploy failed. Look at the rest of the message. |
| `The agent is offline. Environment variables can only be viewed or changed while it is connected.` | The values only exist on the agent. Bring it back online. |
