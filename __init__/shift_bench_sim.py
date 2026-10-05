"""Dry-run manual-transmission shift harness; it does not control hardware."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


VALID_GEARS = {-1, 0, 1, 2, 3, 4, 5, 6}
GEAR_NAMES = {-1: "R", 0: "N", **{gear: str(gear) for gear in range(1, 7)}}
REVERSE_MAX_SPEED_KPH = 0.5


class ShiftRejected(ValueError):
    """Raised when a simulated shift violates a bench interlock."""


@dataclass
class ShiftBench:
    gear: int = 0
    clutch_pressed: bool = False
    speed_kph: float = 0.0

    def __post_init__(self) -> None:
        if self.gear not in VALID_GEARS:
            raise ValueError(f"unsupported starting gear: {self.gear}")
        if self.speed_kph < 0:
            raise ValueError("speed_kph must be non-negative")

    def shift_to(self, target: int) -> list[str]:
        if target not in VALID_GEARS:
            raise ShiftRejected(f"unsupported target gear: {target}")
        if not self.clutch_pressed:
            raise ShiftRejected("clutch interlock: clutch must be pressed")
        if target == -1 and self.speed_kph > REVERSE_MAX_SPEED_KPH:
            raise ShiftRejected(
                f"reverse interlock: speed must be at most {REVERSE_MAX_SPEED_KPH} km/h"
            )
        if self.gear == target:
            return [f"already in gear {GEAR_NAMES[target]}"]

        previous = self.gear
        events = []
        if previous != 0:
            self.gear = 0
            events.append(f"simulated shift {GEAR_NAMES[previous]} -> N")
        if target != 0:
            self.gear = target
            events.append(f"simulated shift N -> {GEAR_NAMES[target]}")
        return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run manual gearbox shift harness")
    parser.add_argument("--gear", type=int, default=0, help="starting gear (-1=R, 0=N, 1-6)")
    parser.add_argument("--target", type=int, required=True, help="requested gear (-1=R, 0=N, 1-6)")
    parser.add_argument("--speed-kph", type=float, default=0.0, help="simulated vehicle speed")
    parser.add_argument("--clutch-pressed", action="store_true", help="simulate clutch interlock")
    args = parser.parse_args()

    try:
        bench = ShiftBench(args.gear, args.clutch_pressed, args.speed_kph)
        events = bench.shift_to(args.target)
    except (ShiftRejected, ValueError) as error:
        parser.error(str(error))

    print("DRY RUN ONLY: no hardware interfaces are present or commanded.")
    for event in events:
        print(event)
    print(f"simulated final gear: {GEAR_NAMES[bench.gear]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())