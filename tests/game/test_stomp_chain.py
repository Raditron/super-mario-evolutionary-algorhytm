"""The stomp chain: stomps without landing climb the original's score table (#17)."""

from mario.simulation.stomp_chain import StompChain

# HandleStompedShellE with FloateyNumTileData / ScoreUpdateData (docs/research/world-1-1-layout.md).
ORIGINAL_STOMP_CHAIN = [100, 200, 400, 500, 800, 1000, 2000, 4000, 5000, 8000]


def stomp_on_separate_ticks(chain: StompChain, stomps: int) -> list[int | None]:
    points = []
    for _ in range(stomps):
        chain.start_tick()
        points.append(chain.stomp())
    return points


def test_consecutive_stomps_without_landing_climb_the_original_score_table():
    assert stomp_on_separate_ticks(StompChain(), 10) == ORIGINAL_STOMP_CHAIN


def test_a_stomp_beyond_the_table_scores_no_points():
    chain = StompChain()
    stomp_on_separate_ticks(chain, 10)
    assert stomp_on_separate_ticks(chain, 2) == [None, None]


def test_landing_restarts_the_chain():
    chain = StompChain()
    stomp_on_separate_ticks(chain, 3)
    chain.land()
    assert stomp_on_separate_ticks(chain, 2) == [100, 200]


def test_a_second_stomp_on_the_same_tick_scores_one_step_higher_and_needs_no_fall():
    chain = StompChain()
    chain.start_tick()
    assert not chain.stomped_this_tick
    assert chain.stomp() == 100
    assert chain.stomped_this_tick
    assert chain.stomp() == 400
    # The same-tick bonus does not carry: the third stomp is the chain's third step.
    chain.start_tick()
    assert not chain.stomped_this_tick
    assert chain.stomp() == 400
