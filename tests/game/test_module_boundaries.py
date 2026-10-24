"""The seams the spec requires (section 3) and the deterministic core (section 4)."""

import ast
import subprocess
import sys
from pathlib import Path

import mario
import mario.constants.physics as physics_constants

PACKAGE_ROOT = Path(mario.__file__).parent
PYGAME_FREE_PACKAGES = ("simulation", "level", "controller")
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


def test_simulation_level_and_controller_never_load_pygame():
    modules = [".".join(("mario",) + path.relative_to(PACKAGE_ROOT).with_suffix("").parts)
               for package in PYGAME_FREE_PACKAGES for path in python_files(package)]
    probe = f"import sys\nfor name in {modules!r}: __import__(name)\nprint('pygame' in sys.modules)"
    loaded = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, check=True)
    assert loaded.stdout.strip() == "False"


def test_simulation_has_no_randomness_wall_clock_or_floats():
    for source_file in python_files("simulation"):
        assert not imported_module_names(source_file) & NONDETERMINISTIC_MODULES, source_file
        for node in ast.walk(ast.parse(source_file.read_text())):
            assert not (isinstance(node, ast.Constant) and isinstance(node.value, float)), source_file
            assert not isinstance(node, ast.Div), f"{source_file}: true division makes floats"


def test_every_physics_constant_is_an_integer():
    constants = {name: value for name, value in vars(physics_constants).items() if name.isupper()}
    assert all(type(value) is int for value in constants.values())
