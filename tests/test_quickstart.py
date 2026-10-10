"""The quickstart guide must name every template field, and nothing that's gone."""

from pathlib import Path

from column_template import load_spec
from column_template.quickstart import check_quickstart, find_drift

SPEC = Path(__file__).parent.parent / "Excel Templates" / "column-ingestion-template.yaml"


def _guide(spec_path: Path) -> str:
    spec = load_spec(spec_path)
    return (spec_path.parent / spec["quickstart"]["guide"]).read_text(encoding="utf-8")


def _units(spec: dict) -> dict:
    return next(sheet for sheet in spec["sheets"] if sheet["name"] == "units")


def test_quickstart_matches_template():
    assert check_quickstart(SPEC) == []


def test_new_field_is_flagged():
    spec = load_spec(SPEC)
    _units(spec)["fields"].append({"name": "grainsize", "kind": "optional"})
    problems = find_drift(spec, _guide(SPEC))
    assert len(problems) == 1
    assert "`grainsize`" in problems[0]


def test_removed_field_is_flagged():
    spec = load_spec(SPEC)
    units = _units(spec)
    units["fields"] = [f for f in units["fields"] if f["name"] != "facies"]
    problems = find_drift(spec, _guide(SPEC))
    assert len(problems) == 1
    assert "`facies`" in problems[0]



def test_expanded_field_is_not_required():
    spec = load_spec(SPEC)
    _units(spec)["fields"].append(
        {"name": "grainsize", "kind": "optional", "only": ["expanded"]}
    )
    assert find_drift(spec, _guide(SPEC)) == []
