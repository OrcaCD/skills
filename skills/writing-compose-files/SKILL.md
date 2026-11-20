---
name: writing-compose-files
description: Write, review and fix Docker Compose files and repository layouts for OrcaCD, the GitOps tool for Docker. Use when creating or changing a compose.yaml in a repository deployed by OrcaCD, when adding a new service or application to such a repository, or when a compose file is rejected by the OrcaCD deployment policy.
---

# Writing compose files for OrcaCD

Requires OrcaCD ≥ 0.6.0.

OrcaCD deploys a compose file from a Git repository to an agent on a Docker host. Most compose files work unchanged, but OrcaCD differs from running `docker compose up` yourself in a few ways. Check every compose file you write or change against this skill.

## How OrcaCD deploys

- **One application is one compose file**: a repository, a branch and a path, deployed by one agent. Several applications can share a repository.
- **Only that file reaches the agent.** OrcaCD reads it through the Git provider's API and writes it to `<DEPLOYMENTS_DIR>/<project>/compose.yaml` on the agent. No other file from the repository is copied: no `.env`, no config files, no Dockerfile, no override files.
- **Relative paths resolve in the application's directory on the agent**, e.g. `./data` becomes `<DEPLOYMENTS_DIR>/<project>/data`. That works well for data directories, but a relative bind mount of a config file from the repository ends up empty.
- **The project name comes from the application name**: lowercased, every character except `a-z`, `0-9` and `_` replaced by `-`.
- **A commit only deploys when the compose file changed.** Commits that only touch other files are recorded but deploy nothing.
- **OrcaCD never builds images.** Build and push images in CI and reference them by tag.
- Services removed from the file are removed on the next deploy (`--remove-orphans`).

## Repository layout

Use one directory per application, so each compose file has room for docs next to it:

```text
apps/
  nextcloud/compose.yaml
  monitoring/compose.yaml
```

With several agents, group by agent instead, e.g. `production/nextcloud/compose.yaml`. The file name must end in `.yml` or `.yaml`.

## Rules the agent enforces

The agent rejects the whole deployment if the file breaks one of these rules. See [references/deployment-policy.md](references/deployment-policy.md) for the exact rules and error messages.

- No `include`, no `extends` with `file:`, no `label_file`: the other files don't exist on the agent. Use `extends` only within the same file.
- No `privileged`, `use_api_socket`, `devices`, `device_cgroup_rules` or `volumes_from`.
- No host namespaces: `network_mode`, `pid`, `ipc`, `uts`, `userns_mode` and `cgroup` must not be `host` or `container:...`. `network_mode: service:<name>` is fine.
- No dangerous `cap_add`, e.g. `ALL`, `SYS_ADMIN`, `NET_ADMIN`, `SYS_PTRACE`. Harmless ones like `NET_BIND_SERVICE` or `CHOWN` are fine.
- `security_opt` only allows `no-new-privileges`.
- No `driver_opts` on volumes, so NFS or CIFS volumes defined that way are rejected.
- Bind mounts, `env_file` and file-based `secrets`/`configs` can't use system paths (`/`, `/etc`, `/usr`, `/var/lib/docker`, the Docker socket, ...), home directories themselves or credential paths below them (`.ssh`, `.aws`, `.docker`, ...), or another application's directory. If the agent sets `RESTRICT_VOLUMES_TO_DEPLOYMENTS_DIR=true`, every host path must be inside the application's own directory.

Don't work around a rejection by suggesting `ALLOWED_PRIVILEGED_APPS`. It turns off all checks for the application and is only meant for tools that really need host access, such as monitoring agents reading the Docker socket. If that's the case, tell the user and let them decide.

## Config files

Since only the compose file reaches the agent, don't mount config files from the repository. Instead, in this order of preference:

1. Put the config inline with a `configs` entry using `content`:

   ```yaml
   services:
     proxy:
       image: caddy:2.10.2
       configs:
         - source: caddyfile
           target: /etc/caddy/Caddyfile
   configs:
     caddyfile:
       content: |
         example.com {
           reverse_proxy app:8080
         }
   ```

2. Configure the service through environment variables.
3. Bake the config into an image built in CI.

## Environment variables and secrets

Never commit secrets to the compose file or the repository. Reference an env file instead:

```yaml
services:
  app:
    image: ghcr.io/example/app:1.4.2
    env_file: .env
```

- The file has to be inside the application's directory. The agent creates it empty on the first deployment, and the user fills in the values in OrcaCD under **Settings → Environment Variables** of the application. They are stored only on the agent.
- `${VAR}` interpolation in the compose file reads the same `.env` file on the agent.
- Entries are secrets unless the line above them is `# orcacd:public`. Secrets can only be replaced, never read back.

Tell the user which variables they need to set after the first deploy. See [Environment Files](https://orcacd.dev/docs/advanced/architecture/environment).

## Images

- Pin a version tag (`postgres:17.6`) or a digest. OrcaCD warns about `latest` and missing tags.
- A Git deploy doesn't pull a moved tag again. To follow a mutable tag like `latest`, enable **Image Polling** or the **Image Pull Webhook** in the application's settings ([docs](https://orcacd.dev/docs/advanced/architecture/applications#image-updates)).
- Images from private registries need `docker login` on the agent host, as the user that starts the agent.

## Health

OrcaCD shows the application's health from the containers, and can roll back deployments that don't become healthy.

- Add a `healthcheck` to services where it makes sense. A running container without one counts as healthy.
- Containers that exit after their work, like migrations or init jobs, count as unhealthy. With automatic rollback on unhealthy deployments, every deploy would be rolled back. Run such tasks in the service's entrypoint instead, or tell the user.
- Set a `restart` policy on long-running services. OrcaCD warns if it's missing.
- Databases need a volume, or their data is lost on the next recreate. OrcaCD warns about this too.

## Other pitfalls

- Don't set the labels `managed_by` or `orca-cd.application-id`. OrcaCD sets them and overwrites yours.
- `profiles` are not activated, so services with a profile don't start.
- Avoid `container_name`, unless needed. It makes the deployment fail if a container with that name already exists on the host.

## Before you commit

1. Run `docker compose -f <file> config --quiet` to check the syntax, if Docker is available.
2. Check the file against the rules above.
3. Tell the user which env variables to set, and which settings to enable in OrcaCD (image polling, rollbacks).
