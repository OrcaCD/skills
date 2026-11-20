---
name: migrating-to-orcacd
description: Move existing Docker Compose deployments to OrcaCD, the GitOps tool for Docker. Use when migrating from manually run docker compose stacks, Portainer stacks or Watchtower to a Git repository deployed by OrcaCD, without losing data.
---

# Migrating to OrcaCD

Requires OrcaCD ≥ 0.6.0.

Migrate one stack at a time. Each stack becomes an OrcaCD application with its compose file in a Git repository. The goal is that the containers move to OrcaCD while the data stays where it is.

The Hub and an agent on the host must already be running. If not, use the `setting-up-orcacd` skill first.

## 1. Take inventory

On the host, collect for every stack:

- **The compose file.** Manual stacks: `docker compose ls` shows each project and its file. Portainer: copy it from the stack's **Editor** tab.
- **The env values.** `.env` files next to the compose file, or the stack's environment variables in Portainer.
- **The project name** (`docker compose ls`). For Portainer stacks it's the stack name.
- **The data**: named volumes (`docker volume ls --filter label=com.docker.compose.project=<project>`) and bind mounts.

## 2. Prepare the compose file

Put the file in the repository, e.g. `apps/<name>/compose.yaml`, and adapt it with the `writing-compose-files` skill. For a migration, pay special attention to:

- **Secrets**: replace inline values with `env_file: .env`. Never commit the values. The user imports them later.
- **Relative bind mounts**: OrcaCD resolves `./data` in the application's directory on the agent, not where the stack ran before. Change data mounts to the absolute host path the data is in today, e.g. `/srv/nextcloud/data`. If the agent has `RESTRICT_VOLUMES_TO_DEPLOYMENTS_DIR=true`, move the data into the application's directory instead.
- **Config files from the stack directory**: inline them with `configs` and `content`. They don't reach the agent otherwise.
- **`build:`**: OrcaCD doesn't build images. Build and push them in CI first.
- **Watchtower**: remove the Watchtower service and its labels (`com.centurylinklabs.watchtower.*`).

Named volumes need no change if the project name stays the same (step 4).

## 3. Commit and push

Commit the compose file and push it. If the repository isn't connected to OrcaCD yet, add it under **Repositories**.

## 4. Switch over

Do this for one stack at a time and tell the user that the application is down between stopping and deploying.

1. Stop the old stack and keep its data:
   - Manual: `docker compose -p <project> down`. Never add `-v`, it deletes the volumes.
   - Portainer: **Stop** the stack (don't delete it yet, so you can go back).
2. In OrcaCD, create the application. Choose a name that gives the same project name: OrcaCD lowercases the name and replaces characters other than `a-z`, `0-9` and `_` with `-`. Then the existing named volumes `<project>_<volume>` are used again. A different project name starts with empty volumes.
3. The first deploy creates the env file empty. In the application's **Settings → Environment Variables**, click **Import** and paste the old `.env`. Untick **Secret** for entries that aren't secret, click **Add to changes** and then **Save & redeploy**.
4. Check that the application is `Synced` and `Healthy`, and that the data is there.

If containers of the old project are still running, OrcaCD refuses to deploy with `compose project "<name>" already exists and is not managed by OrcaCD`. Stop them first.

## 5. Replace Watchtower

Watchtower and OrcaCD both recreating containers leads to surprises. Once all stacks are migrated, remove Watchtower and enable updates per application in **Settings → Image Updates**:

- **Image Polling** checks the registry like Watchtower, every 120 seconds by default.
- **Image Pull Webhook** updates right after the registry gets a new image.

Better still, pin version tags and update them with commits, e.g. with Renovate or Dependabot. Then every update is reviewed and can be rolled back.

## 6. Clean up

Once the application runs fine under OrcaCD:

- Portainer: delete the stopped stack. Its named volumes are now used by the OrcaCD containers, so Docker keeps them.
- Delete the old compose and `.env` files from the host. The `.env` contains secrets.

## Going back

If something goes wrong, delete the application in OrcaCD while its agent is online. This removes its containers and its directory on the agent, but not named volumes or absolute bind mounts. Then start the old stack again.
