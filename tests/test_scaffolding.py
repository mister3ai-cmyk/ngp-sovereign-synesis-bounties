"""Structural tests for the 2026-2027 roadmap modules.

These check that the scaffolding stays coherent: configs parse, stubs import,
every module carries its own licence, and the claim-discipline rules in the
module docstrings are not quietly dropped by a later edit.

They do not test scientific results — there are none yet.

Run: pytest tests/test_scaffolding.py -v
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

yaml = pytest.importorskip("yaml")

ROOT = pathlib.Path(__file__).resolve().parent.parent

MODULES = [
    ROOT / "core" / "sirt6_resonance",
    ROOT / "models" / "dunedin_pace",
    ROOT / "models" / "chipseq_triage",
    ROOT / "safety" / "paleo_shield",
]

STUBS = [
    ROOT / "core" / "sirt6_resonance" / "dock_pocket.py",
    ROOT / "core" / "sirt6_resonance" / "normal_modes.py",
    ROOT / "models" / "dunedin_pace" / "run_pace.py",
    ROOT / "models" / "chipseq_triage" / "triage.py",
    ROOT / "safety" / "paleo_shield" / "criteria.py",
]

CONFIGS = sorted(
    p for module in MODULES for p in (module / "config").glob("*.yaml")
)

# Words that would turn a computational module into a medical or safety claim.
FORBIDDEN = ("cure", "guaranteed", "safety verified", "proven safe", "treats patients")


@pytest.mark.parametrize("module", MODULES, ids=lambda p: p.name)
def test_module_has_readme_and_licence(module: pathlib.Path) -> None:
    assert (module / "README.md").is_file(), f"{module} is missing README.md"
    licence = module / "LICENSE"
    assert licence.is_file(), f"{module} is missing its own LICENSE"
    assert "Apache License" in licence.read_text(encoding="utf-8")


@pytest.mark.parametrize("config", CONFIGS, ids=lambda p: f"{p.parent.parent.name}/{p.name}")
def test_config_parses(config: pathlib.Path) -> None:
    data = yaml.safe_load(config.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{config} did not parse to a mapping"
    assert "output_dir" in data, f"{config} must declare output_dir"


def load_stub(stub: pathlib.Path):
    """Import a stub by path.

    The module is registered in sys.modules before execution because
    dataclasses resolve annotations through sys.modules at class-creation time.
    """
    spec = importlib.util.spec_from_file_location(stub.stem, stub)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


@pytest.mark.parametrize("stub", STUBS, ids=lambda p: p.name)
def test_stub_imports(stub: pathlib.Path) -> None:
    """Each stub must import cleanly; a broken stub is worse than no stub."""
    module = load_stub(stub)
    assert module.__doc__, f"{stub.name} has no module docstring"


@pytest.mark.parametrize("stub", STUBS, ids=lambda p: p.name)
def test_no_overclaiming_language(stub: pathlib.Path) -> None:
    text = stub.read_text(encoding="utf-8").lower()
    found = [w for w in FORBIDDEN if w in text]
    assert not found, f"{stub.name} contains claim language: {found}"


def test_roadmap_exists_and_links_every_module() -> None:
    roadmap = ROOT / "docs" / "ROADMAP_2026_2027.md"
    assert roadmap.is_file()
    text = roadmap.read_text(encoding="utf-8")
    for module in MODULES:
        rel = module.relative_to(ROOT).as_posix()
        assert rel in text, f"roadmap does not reference {rel}"


def test_paleo_shield_states_it_is_not_a_safety_assessment() -> None:
    """The disclaimer is load-bearing; fail loudly if an edit removes it."""
    limitations = ROOT / "safety" / "paleo_shield" / "LIMITATIONS.md"
    assert limitations.is_file(), "LIMITATIONS.md must exist"
    assert "does not verify safety" in limitations.read_text(encoding="utf-8").lower()

    readme = (ROOT / "safety" / "paleo_shield" / "README.md").read_text(encoding="utf-8")
    assert "does not verify safety" in readme.lower()


def test_paleo_shield_refuses_unsourced_thresholds() -> None:
    """A threshold without a citation must not be applied silently."""
    criteria = load_stub(ROOT / "safety" / "paleo_shield" / "criteria.py")

    with pytest.raises(criteria.UnsourcedThreshold):
        criteria.evaluate({"nanog_expression": 0.9})


def test_dunedin_pace_keeps_the_gpl_boundary() -> None:
    """The GPL-3.0 reference implementation must stay an external process."""
    source = (ROOT / "models" / "dunedin_pace" / "run_pace.py").read_text(encoding="utf-8")
    assert "import DunedinPACE" not in source
    assert "subprocess" in source, "reference implementation must be invoked as a process"

    config = yaml.safe_load(
        (ROOT / "models" / "dunedin_pace" / "config" / "cohorts.yaml").read_text(encoding="utf-8")
    )
    assert config["reference_implementation"]["invocation"] == "external_process"
    assert config["reference_implementation"]["license"] == "GPL-3.0"
