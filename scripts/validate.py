#!/usr/bin/env python3
"""Repository checks that the plugin and skill validators don't cover.

- The Claude Code and Codex manifests describe the same plugin.
- No manifest sets a version, so every commit to main reaches users.
- Paths in the Codex manifest are valid; Codex silently ignores broken ones.
- Every skill states its minimum OrcaCD version and is listed in the README.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "orcacd"
REQUIRES_RE = re.compile(r"^Requires OrcaCD ≥ \d+\.\d+(\.\d+)?\.?$", re.MULTILINE)

errors: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def load(path: str) -> dict:
    try:
        return json.loads((ROOT / path).read_text())
    except (OSError, json.JSONDecodeError) as e:
        error(f"{path}: {e}")
        return {}


def check_manifests() -> None:
    claude = load(".claude-plugin/plugin.json")
    codex = load(".codex-plugin/plugin.json")
    claude_mp = load(".claude-plugin/marketplace.json")
    codex_mp = load(".agents/plugins/marketplace.json")

    for path, manifest in [(".claude-plugin/plugin.json", claude), (".codex-plugin/plugin.json", codex)]:
        if manifest.get("name") != PLUGIN_NAME:
            error(f"{path}: name must be {PLUGIN_NAME!r}")
        if "version" in manifest:
            error(f"{path}: remove 'version', see AGENTS.md")

    for field in ("description", "keywords"):
        if claude.get(field) != codex.get(field):
            error(f"{field} differs between .claude-plugin/plugin.json and .codex-plugin/plugin.json")

    for path, marketplace in [(".claude-plugin/marketplace.json", claude_mp), (".agents/plugins/marketplace.json", codex_mp)]:
        if marketplace.get("name") != PLUGIN_NAME:
            error(f"{path}: name must be {PLUGIN_NAME!r}")
        names = [p.get("name") for p in marketplace.get("plugins", [])]
        if names != [PLUGIN_NAME]:
            error(f"{path}: must list exactly one plugin named {PLUGIN_NAME!r}, found {names}")
        for plugin in marketplace.get("plugins", []):
            if "version" in plugin:
                error(f"{path}: remove 'version' from plugin {plugin.get('name')!r}, see AGENTS.md")

    paths = [("skills", codex.get("skills"))]
    paths += [(f"interface.{k}", codex.get("interface", {}).get(k)) for k in ("composerIcon", "logo")]
    for field, value in paths:
        if value is None:
            continue
        if not value.startswith("./") or not (ROOT / value).exists():
            error(f".codex-plugin/plugin.json: {field} must be an existing path starting with './', got {value!r}")

    icon = claude.get("icon")
    if icon and not (ROOT / icon).is_file():
        error(f".claude-plugin/plugin.json: icon {icon!r} does not exist")


def check_skills() -> None:
    readme = (ROOT / "README.md").read_text()
    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())

    for skill in skills:
        rel = skill.relative_to(ROOT)
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            error(f"{rel}: missing SKILL.md")
            continue
        if not REQUIRES_RE.search(skill_md.read_text()):
            error(f"{rel}/SKILL.md: missing a 'Requires OrcaCD ≥ x.y' line")
        if f"]({rel}/SKILL.md)" not in readme:
            error(f"README.md: add {skill.name} to the skills table, linking to {rel}/SKILL.md")

    for link in re.findall(r"\]\((skills/[^)]+)\)", readme):
        if not (ROOT / link).exists():
            error(f"README.md: link to {link} does not exist")


def main() -> int:
    check_manifests()
    check_skills()
    for msg in errors:
        print(f"error: {msg}", file=sys.stderr)
    if errors:
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
