"""
Passenger Modeling & Stochastic Traffic Generation
Implements Poisson Arrival Processes for Up-Peak, Down-Peak, and Inter-Floor Regimes.
"""

import random
from dataclasses import dataclass
from typing import Optional, List
from config import Direction, TrafficMode, SimulationConfig

@dataclass
class Passenger:
    id: int
    origin_floor: int
    dest_floor: int
    call_time: float
    board_time: Optional[float] = None
    exit_time: Optional[float] = None
    assigned_elevator: Optional[int] = None

    @property
    def direction(self) -> Direction:
        if self.dest_floor > self.origin_floor:
            return Direction.UP
        elif self.dest_floor < self.origin_floor:
            return Direction.DOWN
        return Direction.NONE

    @property
    def wait_time(self) -> float:
        """Waiting time at the floor before boarding."""
        if self.board_time is not None:
            return self.board_time - self.call_time
        return 0.0

    @property
    def journey_time(self) -> float:
        """In-car transit time from boarding to exit."""
        if self.exit_time is not None and self.board_time is not None:
            return self.exit_time - self.board_time
        return 0.0

    @property
    def total_turnaround_time(self) -> float:
        """Total time from pushing hall button to reaching destination."""
        if self.exit_time is not None:
            return self.exit_time - self.call_time
        return 0.0


class TrafficGenerator:
    """Generates stochastic passenger flows according to non-stationary Poisson processes."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self._next_id = 1

    def generate_passengers(self, current_time: float, dt: float) -> List[Passenger]:
        """
        Determines how many passengers arrive in time interval dt using Poisson distribution:
        P(k arrivals) = (lambda * dt)^k * exp(-lambda * dt) / k!
        """
        expected_arrivals = self.config.arrival_rate_lambda * dt
        # Poisson approximation using numpy or knuth algorithm
        num_arrivals = 0
        p = 1.0
        limit = random.expovariate(1.0) if expected_arrivals > 0 else 999.0
        
        # Fast Poisson draw
        num_arrivals = random.choices(
            [0, 1, 2, 3],
            weights=[
                max(0.01, 1.0 - expected_arrivals),
                expected_arrivals,
                (expected_arrivals ** 2) / 2.0,
                (expected_arrivals ** 3) / 6.0
            ]
        )[0]

        passengers: List[Passenger] = []
        for _ in range(num_arrivals):
            origin, dest = self._sample_origin_dest()
            p = Passenger(
                id=self._next_id,
                origin_floor=origin,
                dest_floor=dest,
                call_time=current_time
            )
            self._next_id += 1
            passengers.append(p)

        return passengers

    def _sample_origin_dest(self) -> tuple[int, int]:
        N = self.config.num_floors
        mode = self.config.traffic_mode

        if mode == TrafficMode.UP_PEAK:
            # 80% Ground Lobby -> Upper floors, 20% Random inter-floor
            if random.random() < 0.80:
                origin = 0
                dest = random.randint(1, N - 1)
            else:
                origin = random.randint(0, N - 1)
                dest = random.choice([f for f in range(N) if f != origin])

        elif mode == TrafficMode.DOWN_PEAK:
            # 80% Upper floors -> Ground Lobby, 20% Random inter-floor
            if random.random() < 0.80:
                origin = random.randint(1, N - 1)
                dest = 0
            else:
                origin = random.randint(0, N - 1)
                dest = random.choice([f for f in range(N) if f != origin])

        else:  # TrafficMode.INTER_FLOOR
            # Uniformly distributed floor pairs
            origin = random.randint(0, N - 1)
            dest = random.choice([f for f in range(N) if f != origin])

        return origin, dest
