"""The seams the spec requires (section 3) and the deterministic core (section 4)."""

import ast
import subprocess
import sys
from pathlib import Path

import mario
import mario.constants.physics as physics_constants

PACKAGE_ROOT = Path(mario.__file__).parent
PYGAME_FREE_PACKAGES = ("simulation", "level", "controller", "training")
USERS_PACKAGE = "neuroevolution"
THE_ONE_IMPORTER_OF_THE_USERS_PACKAGE = PACKAGE_ROOT / "modes" / "train_mode.py"
NONDETERMINISTIC_MODULES = {"random", "time", "datetime", "secrets", "uuid"}


def python_files(package: str) -> list[Path]:
    return sorted((PACKAGE_ROOT / package).rglob("*.py"))


def imported_module_names(source_file: Path) -> set[str]:
    tree = ast.parse(source_file.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_simulation_level_controller_and_training_never_load_pygame():
    modules = [".".join(("mario",) + path.relative_to(PACKAGE_ROOT).with_suffix("").parts)
               for package in PYGAME_FREE_PACKAGES for path in python_files(package)]
    modules.append("mario.modes.train_mode")
    probe = f"import sys\nfor name in {modules!r}: __import__(name)\nprint('pygame' in sys.modules)"
    loaded = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, check=True)
    assert loaded.stdout.strip() == "False"


def test_only_train_mode_imports_the_users_package():
    importers = [source_file for source_file in sorted(PACKAGE_ROOT.rglob("*.py"))
                 if USERS_PACKAGE in imported_module_names(source_file)]
    assert importers == [THE_ONE_IMPORTER_OF_THE_USERS_PACKAGE]


def test_simulation_has_no_randomness_wall_clock_or_floats():
    """Attempt state is integers only. The one exception is ObservationBuilder: it
    turns that integer state into float64 only at its output, the Observation, and
    no float may ever flow back into Attempt state. It divides with numpy, which
    this check doesn't see, so the rule rests on that boundary staying put."""
    for source_file in python_files("simulation"):
        assert not imported_module_names(source_file) & NONDETERMINISTIC_MODULES, source_file
        for node in ast.walk(ast.parse(source_file.read_text())):
            assert not (isinstance(node, ast.Constant) and isinstance(node.value, float)), source_file
            assert not isinstance(node, ast.Div), f"{source_file}: true division makes floats"


def test_every_physics_constant_is_an_integer():
    constants = {name: value for name, value in vars(physics_constants).items() if name.isupper()}
    assert all(type(value) is int for value in constants.values())
