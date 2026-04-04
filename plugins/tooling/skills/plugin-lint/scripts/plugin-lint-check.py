#!/usr/bin/env python3
"""
Checks déterministes du skill plugin-lint (conventions + liens bundlés).

Emplacement : même dossier que SKILL.md, sous `scripts/` (fichiers de support
officiels — https://code.claude.com/docs/fr/skills#ajouter-des-fichiers-de-support ).

À lancer depuis la racine du dépôt (CLAUDE_PROJECT_DIR ou cwd) : hook pre-commit,
CI, ou manuellement :
  python3 "${CLAUDE_SKILL_DIR}/scripts/plugin-lint-check.py"

Sortie : 0 = OK, 2 = bloquant (hook Claude Code).
Le rapport sémantique (secrets, nuance) reste le SKILL.md interactif.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

EXIT_BLOCK = 2
MAX_SKILL_LINES = 500

# Chemins bundlés réels (extension obligatoire — évite « references/... » dans le prose)
BUNDLED_PREFIX = re.compile(
    r"\$\{CLAUDE_SKILL_DIR\}/(references|examples|scripts)/([a-zA-Z0-9_./\-]+\.(?:md|sh|json|mjs|ts|tsx|js|yaml|yml|txt))"
)

# Exemples illustratifs dans le texte (pas des fichiers du repo)
_PLACEHOLDER_FILES = frozenset(
    {"foo.md", "bar.md", "baz.md", "example.md", "placeholder.md"}
)


def fail(msg: str) -> None:
    print(f"plugin-lint-check: {msg}", file=sys.stderr)
    sys.exit(EXIT_BLOCK)


def _has_skill_name(text: str) -> bool:
    """## name: (style plugin-lint) ou name: dans le premier bloc YAML --- ... ---."""
    if re.search(r"(?m)^## name:\s*\S+", text):
        return True
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if m and re.search(r"(?m)^name:\s*\S+", m.group(1)):
        return True
    return False


def main() -> None:
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())).resolve()
    os.chdir(root)

    check_marketplace(root)
    plugin_manifests = list(root.glob("plugins/*/.claude-plugin/plugin.json"))
    for manifest in plugin_manifests:
        check_plugin_json(manifest)

    for skill_md in root.glob("plugins/*/skills/*/SKILL.md"):
        check_skill_md(skill_md)

    skip_git = os.environ.get("PLUGIN_LINT_CHECK_SKIP_GIT", "") == "1"
    if not skip_git:
        check_staged_version_bumps(root)


def check_marketplace(root: Path) -> None:
    path = root / ".claude-plugin" / "marketplace.json"
    if not path.is_file():
        return
    import json

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{path}: JSON invalide — {e}")

    for key in ("name", "plugins"):
        if key not in data:
            fail(f"{path}: clé manquante {key!r}")
    if not isinstance(data["plugins"], list):
        fail(f"{path}: plugins doit être un tableau")
    for i, p in enumerate(data["plugins"]):
        if not isinstance(p, dict):
            fail(f"{path}: plugins[{i}] doit être un objet")
        for key in ("name", "source"):
            if key not in p:
                fail(f"{path}: plugins[{i}] manque {key!r}")
        src = p["source"]
        resolved = (root / src.lstrip("./")).resolve()
        if not resolved.is_dir():
            fail(f"{path}: plugins[{i}] source inexistant — {src}")


def check_plugin_json(path: Path) -> None:
    import json

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{path}: JSON invalide — {e}")
    for key in ("name", "version", "description"):
        if key not in data:
            fail(f"{path}: clé manquante {key!r}")
    ver = data["version"]
    if not isinstance(ver, str) or not ver.strip():
        fail(f"{path}: version doit être une chaîne non vide")


def check_skill_md(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > MAX_SKILL_LINES:
        fail(f"{path}: {len(lines)} lignes — max {MAX_SKILL_LINES} (conventions)")

    if "## Gotchas" not in text:
        fail(f"{path}: section « ## Gotchas » absente (conventions)")

    if not _has_skill_name(text):
        fail(
            f"{path}: identifiant de skill manquant — « ## name: … » ou frontmatter YAML « name: »"
        )

    skill_dir = path.parent
    for m in BUNDLED_PREFIX.finditer(text):
        rel = f"{m.group(1)}/{m.group(2)}"
        base = Path(rel).name
        if base in _PLACEHOLDER_FILES:
            continue
        target = (skill_dir / rel).resolve()
        try:
            target.relative_to(skill_dir.resolve())
        except ValueError:
            fail(f"{path}: chemin bundlé hors du skill — {rel}")
        if not target.is_file():
            fail(f"{path}: lien mort ${{CLAUDE_SKILL_DIR}}/{rel}")


def check_staged_version_bumps(root: Path) -> None:
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        fail(f"git indisponible — {e}")

    if out.returncode != 0:
        fail(f"git diff --cached a échoué: {out.stderr.strip()}")

    staged = [p.strip() for p in out.stdout.splitlines() if p.strip()]
    if not staged:
        return

    plugins_touched: set[str] = set()
    for p in staged:
        parts = p.split("/")
        if len(parts) >= 2 and parts[0] == "plugins":
            plugins_touched.add(parts[1])

    for name in sorted(plugins_touched):
        prefix = f"plugins/{name}/"
        manifest = f"plugins/{name}/.claude-plugin/plugin.json"
        other = [p for p in staged if p.startswith(prefix) and p != manifest]
        if not other:
            continue
        if manifest not in staged:
            fail(
                f"bump requis: fichiers modifiés sous {prefix!r} mais {manifest} "
                f"absent du staging — incrémente la version (CLAUDE.md / conventions)."
            )


if __name__ == "__main__":
    main()
