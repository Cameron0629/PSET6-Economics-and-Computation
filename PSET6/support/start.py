#!/usr/bin/env python3

"""Generate team-specific starter files for the programming assignment."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TEAM_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def generated_class_name(teamname: str, suffix: str) -> str:
    """Return the class name corresponding to a generated module."""
    module_name = f"{teamname.lower()}{suffix}"
    return module_name[0].upper() + module_name[1:]


def render_template(template: str, class_name: str) -> str:
    marker = "class BBAgent:"
    if marker not in template:
        raise RuntimeError("Could not find the BBAgent class in bbagent_template.py")
    return template.replace(marker, f"class {class_name}:", 1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create TEAMNAMEbb.py and TEAMNAMEbudget.py starter files."
    )
    parser.add_argument("teamname", help="A short Python identifier for your team")
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing generated files",
    )
    args = parser.parse_args()

    if not TEAM_RE.fullmatch(args.teamname):
        parser.error(
            "TEAMNAME must start with a letter and contain only letters, digits, or underscores."
        )

    teamname = args.teamname.lower()
    script_dir = Path(__file__).resolve().parent
    template_path = script_dir / "bbagent_template.py"
    template = template_path.read_text(encoding="utf-8")

    outputs = []
    for suffix in ("bb", "budget"):
        path = Path.cwd() / f"{teamname}{suffix}.py"
        class_name = generated_class_name(teamname, suffix)
        outputs.append((path, class_name))

    existing = [path for path, _ in outputs if path.exists()]
    if existing and not args.force:
        names = ", ".join(path.name for path in existing)
        parser.error(
            f"Refusing to overwrite existing file(s): {names}. "
            "Use --force only if you intentionally want to replace them."
        )

    for path, class_name in outputs:
        path.write_text(render_template(template, class_name), encoding="utf-8")
        print(f"Created {path.name} with class {class_name}.")

    print("All done. Code away!")
    print(f"Run `python3 test_bb.py {teamname}` after implementing balanced bidding.")


if __name__ == "__main__":
    main()
