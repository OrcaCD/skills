# OrcaCD deployment policy

The agent checks every compose file before it deploys it, and again before every image update. If a check fails, the deployment is rejected and the previous compose file stays in place. All violations are reported together:

```text
deployment rejected by security policy: compose project violates deployment security policy: service "app": privileged mode is not allowed; ... (add application id "<id>" to ALLOWED_PRIVILEGED_APPS to bypass all security policy checks)
```

User-facing docs: [Compose deployment policy](https://orcacd.dev/docs/advanced/security#compose-deployment-policy).

## Rejected before the policy runs

| Setting | Error |
| --- | --- |
| Top-level `include`, `extends` with `file:`, `label_file` | `unsupported Compose feature "<feature>" in service "<service>": local Compose references are not resolved; deployment was rejected` |
| Invalid YAML or compose schema | `load compose project: ...` |
| Empty file | `compose file is empty` |

## Service settings

| Setting | Error |
| --- | --- |
| `privileged: true` | `privileged mode is not allowed` |
| `use_api_socket: true` | `use_api_socket is not allowed` |
| `cap_add`: `ALL`, `SYS_ADMIN`, `SYS_MODULE`, `SYS_PTRACE`, `SYS_RAWIO`, `SYS_BOOT`, `NET_ADMIN`, `BPF`, `PERFMON`, `DAC_READ_SEARCH`, `DAC_OVERRIDE`, `MAC_ADMIN`, `MAC_OVERRIDE` | `cap_add "<cap>" is not allowed` |
| `network_mode`, `pid`, `ipc`, `uts`, `userns_mode`, `cgroup` set to `host` | `<field>: host is not allowed` |
| The same fields set to `container:<name>` | `<field>: joining another container's namespace is not allowed` |
| `devices` | `device mappings are not allowed` |
| `device_cgroup_rules` | `device_cgroup_rules are not allowed` |
| `volumes_from` | `volumes_from is not allowed` |
| `security_opt` other than `no-new-privileges` | `security_opt "<value>" is not allowed` |
| `provider` services | `provider services are not allowed` |
| Privileged `post_start`/`pre_stop` hooks | `privileged hooks are not allowed` |
| Top-level volume with `driver_opts` | `volume "<name>": driver_opts are not allowed` |

Not checked at all: `ports`, `container_name`, `healthcheck`, `profiles`, named volumes without `driver_opts`, other capabilities.

## Host paths

These rules apply to bind mount sources, `env_file` paths and file-based top-level `secrets` and `configs`. Errors look like `service "<service>": bind mount source "<path>" <reason>`.

| Path | Reason in the error |
| --- | --- |
| `/`, `/etc`, `/boot`, `/root`, `/sys`, `/proc`, `/usr`, `/bin`, `/sbin`, `/lib`, `/lib64`, `/dev`, `/run`, `/var/run`, `/var/lib/docker`, `/var/lib/containerd`, the Docker socket, and paths below them | `is under sensitive host path "<path>", which is not allowed` |
| Parents of these paths | `contains sensitive host path "<path>", which is not allowed` |
| `/home` and `/home/<user>` | `is a home directory, which contains sensitive paths` |
| Paths below `/home` containing `.ssh`, `.aws`, `.kube`, `.docker`, `.gnupg`, `id_*`, `authorized_keys`, ... | `contains sensitive path component "<name>"` |
| A parent of the agent's deployments directory | `contains the deployments directory of the agent, which holds the files of other applications` |
| Another application's directory | `is inside the deployments directory but outside the application's directory "<dir>"` |
| A path through a symlink | `traverses symlink "<path>", which is not allowed` |
| A path the agent can't inspect | `could not be checked for symlinks: ...` |
| Anything outside the application's directory, with `RESTRICT_VOLUMES_TO_DEPLOYMENTS_DIR=true` | `is not inside the agent's deployment directory "<dir>"` |

Everything else is allowed, e.g. `/srv`, `/opt`, `/mnt` or `/home/<user>/data`.

For `could not be checked for symlinks ... permission denied`, see [Common Issues](https://orcacd.dev/docs/troubleshooting/common-issues#deployment-fails-with-permission-denied-during-symlink-checks).

## Warnings

The agent also reports warnings under **Compose configuration warnings** on the application's details page. Only privileged, host network and host namespace warnings are also rejected by the policy. The others don't block the deployment:

| Code | Meaning |
| --- | --- |
| `missing_restart_policy` | A service has no `restart` policy |
| `database_without_volume` | A database image has no volume for its data |
| `floating_image_reference` | An image has no tag or uses `latest` |
| `privileged_container`, `host_network`, `host_namespace` | Rejected by the policy, see above |
| `invalid_compose`, `unsupported_compose_feature` | The file can't be loaded, see above |
