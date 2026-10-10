"""Check that the quickstart guide still matches the template's fields.

The guide is written by hand, so it is checked rather than regenerated:

- every field of the guide's template (`quickstart.template` in the YAML) must be
  named (in backticks) in the guide's section for its tab, unless the field is
  marked `quickstart: false`; fields only in other templates are left to them;
- every field the guide lists in the first column of a table must still exist on
  that tab in the YAML.

Run with `python -m column_template.quickstart SPEC.yaml`; exits non-zero on drift.
"""

import re
import sys
from pathlib import Path

from .builder import included, load_spec

_FIELD = re.compile(r"`([a-z_]+)`")


def _sections(guide: str) -> dict[str, str]:
    """The guide's `## ...` sections, keyed by the tab named in the heading."""
    sections, name, lines = {}, None, []
    for line in guide.splitlines():
        if line.startswith("## "):
            if name is not None:
                sections[name] = "\n".join(lines)
            match = _FIELD.search(line)
            name = match.group(1) if match else None
            lines = []
        elif name is not None:
            lines.append(line)
    if name is not None:
        sections[name] = "\n".join(lines)
    return sections


def _table_fields(section: str) -> list[str]:
    """Field names in the first column of the section's tables."""
    names = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        first_cell = line.strip("|").split("|")[0]
        names.extend(_FIELD.findall(first_cell))
    return names


def _fields(sheet: dict) -> list[dict]:
    """The fields or metadata keys on a tab."""
    return sheet.get("fields") or sheet.get("rows") or []


def _name(entry: dict) -> str:
    return entry.get("name") or entry["key"]


def find_drift(spec: dict, guide: str) -> list[str]:
    """Problems that mean the guide no longer matches the template."""
    sections = _sections(guide)
    template = spec["quickstart"]["template"]
    problems = []
    for sheet in spec["sheets"]:
        if sheet.get("layout") == "list" or sheet.get("quickstart") is False:
            continue
        tab = sheet["name"]
        section = sections.get(tab)
        if section is None:
            problems.append(
                f"The quickstart has no section for the `{tab}` tab. Add one, or mark the "
                f"tab `quickstart: false` in the YAML."
            )
            continue
        mentioned = set(_FIELD.findall(section))
        fields = _fields(sheet)
        for entry in fields:
            name = _name(entry)
            documented = entry.get("quickstart", True)
            if documented and included(entry, template) and name not in mentioned:
                problems.append(
                    f"`{name}` (on the `{tab}` tab) is not mentioned in the quickstart's "
                    f"`{tab}` section. Document it there, or mark it `quickstart: false` "
                    f"in the YAML."
                )
        names = {_name(entry) for entry in fields}
        for name in _table_fields(section):
            if name not in names:
                problems.append(
                    f"The quickstart's `{tab}` section lists `{name}`, which is no longer a "
                    f"field on that tab in the YAML. Update or remove it."
                )
    return problems


def check_quickstart(spec_path, guide_path=None) -> list[str]:
    """`find_drift` for files: the guide defaults to the spec's `quickstart.guide` path."""
    spec_path = Path(spec_path)
    spec = load_spec(spec_path)
    if guide_path is None:
        guide_path = spec_path.parent / spec["quickstart"]["guide"]
    return find_drift(spec, Path(guide_path).read_text(encoding="utf-8"))


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        sys.exit("usage: python -m column_template.quickstart SPEC.yaml")
    problems = check_quickstart(args[0])
    if problems:
        print("The quickstart guide is out of date with the template:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)
    print("Quickstart guide matches the template.")


if __name__ == "__main__":
    main()
