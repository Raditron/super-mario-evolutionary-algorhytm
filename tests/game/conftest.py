import pytest

from mario.level.static_level import StaticLevel
from tests.game.helpers import build_level


@pytest.fixture(scope="session")
def world_1_1() -> StaticLevel:
    return StaticLevel.load_world_1_1()


@pytest.fixture
def flat_level() -> StaticLevel:
    return build_level()
