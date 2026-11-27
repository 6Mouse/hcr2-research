"""Run HCR2-003 with `python replay_drift_fixture.py`."""

from math import hypot, sin
from typing import Iterable, Iterator


INJECTION_DISTANCE_M = 16_000
REPLAY_LENGTH_M = 20_000
LATERAL_OFFSET_M = 8
MAX_STEP_M = 2

Point = tuple[int, float]


def trajectory(*, inject_jump: bool) -> Iterator[Point]:
    """Generate one sample per meter with a smooth lateral coordinate."""
    for distance_m in range(REPLAY_LENGTH_M + 1):
        lateral_m = 3 * sin(distance_m / 50)
        if inject_jump and distance_m >= INJECTION_DISTANCE_M:
            lateral_m += LATERAL_OFFSET_M
        yield distance_m, lateral_m


def detect_discontinuities(points: Iterable[Point]) -> list[int]:
    """Return the distance of the later sample in each oversized step."""
    samples = iter(points)
    previous = next(samples, None)
    jumps = []
    for distance_m, lateral_m in samples:
        previous_distance_m, previous_lateral_m = previous
        step_m = hypot(distance_m - previous_distance_m, lateral_m - previous_lateral_m)
        if step_m > MAX_STEP_M:
            jumps.append(distance_m)
        previous = distance_m, lateral_m
    return jumps


def main() -> int:
    control = detect_discontinuities(trajectory(inject_jump=False))
    injected = detect_discontinuities(trajectory(inject_jump=True))
    print(f"Continuous control discontinuities (m): {control}")
    print(f"Injected trajectory discontinuities (m): {injected}")
    if control or injected != [INJECTION_DISTANCE_M]:
        print("FAIL: expected a clean control and exactly one jump at 16 km")
        return 1
    print("PASS: continuous control and 16 km discontinuity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
