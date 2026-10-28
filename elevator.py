"""
Elevator Car Agent & Kinematic Finite State Machine (FSM)
Simulates realistic micro-motion, physical velocity curves, door cycles, and passenger boarding.
"""

from typing import List, Set, Optional, Tuple
from config import Direction, ElevatorState, SimulationConfig
from passenger import Passenger

class ElevatorCar:
    """Autonomous Car Agent operating a localized 7-State Kinematic FSM."""

    def __init__(self, car_id: int, config: SimulationConfig):
        self.car_id = car_id
        self.config = config

        # Kinematic State Variables
        self.current_floor_pos: float = 0.0    # Continuous floor position (e.g. 4.25)
        self.velocity: float = 0.0             # Current speed in meters/second
        self.direction: Direction = Direction.NONE
        self.state: ElevatorState = ElevatorState.IDLE

        # Call Queues & Passenger Manifest
        self.passengers: List[Passenger] = []
        self.assigned_hall_calls: Set[Tuple[int, Direction]] = set() # (floor, direction)
        self.car_calls: Set[int] = set()       # Destination floors pressed onboard
        self.parking_target_floor: Optional[int] = None # Proactive parking target

        # Timers & Physical Telemetry
        self.door_timer: float = 0.0
        self.total_travel_meters: float = 0.0
        self.door_cycles: int = 0
        self.reversal_count: int = 0
        self.idle_time: float = 0.0

    @property
    def current_floor_int(self) -> int:
        return int(round(self.current_floor_pos))

    @property
    def load_count(self) -> int:
        return len(self.passengers)

    @property
    def is_full(self) -> bool:
        return self.load_count >= self.config.car_capacity

    @property
    def capacity_ratio(self) -> float:
        return self.load_count / max(1, self.config.car_capacity)

    @property
    def all_target_floors(self) -> Set[int]:
        targets = set(self.car_calls)
        # If car is full, prioritize discharging onboard passengers only!
        if not self.is_full:
            for f, _ in self.assigned_hall_calls:
                targets.add(f)
            if self.parking_target_floor is not None and not targets:
                targets.add(self.parking_target_floor)
        return targets

    def update(self, dt: float, current_time: float, floor_queues: dict) -> List[Passenger]:
        """
        Executes one kinematic tick (dt seconds).
        Returns a list of passengers who exited the elevator during this tick.
        """
        exited_passengers: List[Passenger] = []

        if self.state == ElevatorState.IDLE:
            self.idle_time += dt
            self.velocity = 0.0

            # If there are waiting passengers right at this floor, immediately open doors to serve!
            waiting_here = floor_queues.get(self.current_floor_int, [])
            if waiting_here and len(self.passengers) < self.config.car_capacity:
                self.state = ElevatorState.DOOR_OPEN
                self.door_timer = self.config.door_operate_time
                return exited_passengers

            next_target = self._select_next_target()
            if next_target is not None:
                if next_target == self.current_floor_int:
                    self.state = ElevatorState.DOOR_OPEN
                    self.door_timer = self.config.door_operate_time
                else:
                    new_dir = Direction.UP if next_target > self.current_floor_pos else Direction.DOWN
                    if self.direction != Direction.NONE and new_dir != self.direction:
                        self.reversal_count += 1
                    self.direction = new_dir
                    self.state = ElevatorState.ACCELERATING

        elif self.state == ElevatorState.ACCELERATING:
            # v = v0 + a * dt
            accel_step = self.config.acceleration * dt
            self.velocity = min(self.config.max_velocity, self.velocity + accel_step)
            self._move(dt)

            target = self._get_next_stop_ahead()
            if target is not None and self._is_time_to_decelerate(target):
                self.state = ElevatorState.DECELERATING
            elif self.velocity >= self.config.max_velocity:
                self.state = ElevatorState.CRUISE

        elif self.state == ElevatorState.CRUISE:
            self.velocity = self.config.max_velocity
            self._move(dt)

            target = self._get_next_stop_ahead()
            if target is not None and self._is_time_to_decelerate(target):
                self.state = ElevatorState.DECELERATING

        elif self.state == ElevatorState.DECELERATING:
            # v = v0 - a * dt
            decel_step = self.config.acceleration * dt
            self.velocity = max(0.1, self.velocity - decel_step)
            self._move(dt)

            target = self._get_next_stop_ahead()
            if target is not None:
                dist_to_floor = abs(self.current_floor_pos - target) * self.config.floor_height_meters
                # Reached floor boundary
                if dist_to_floor < 0.15 or (self.direction == Direction.UP and self.current_floor_pos >= target) or \
                   (self.direction == Direction.DOWN and self.current_floor_pos <= target):
                    self.current_floor_pos = float(target)
                    self.velocity = 0.0
                    self.state = ElevatorState.DOOR_OPEN
                    self.door_timer = self.config.door_operate_time

        elif self.state == ElevatorState.DOOR_OPEN:
            self.door_timer -= dt
            if self.door_timer <= 0.0:
                self.door_cycles += 1
                self.state = ElevatorState.SERVICING
                # Perform passenger exchange and compute dwell time
                boarded, exited = self._service_passengers(current_time, floor_queues)
                exited_passengers.extend(exited)
                transfers = len(boarded) + len(exited)
                self.door_timer = self.config.door_dwell_time + (transfers * self.config.passenger_transfer_time)

        elif self.state == ElevatorState.SERVICING:
            self.door_timer -= dt
            if self.door_timer <= 0.0:
                self.state = ElevatorState.DOOR_CLOSE
                self.door_timer = self.config.door_operate_time

        elif self.state == ElevatorState.DOOR_CLOSE:
            self.door_timer -= dt
            if self.door_timer <= 0.0:
                # Remove current floor from calls
                curr_f = self.current_floor_int
                self.car_calls.discard(curr_f)
                self.assigned_hall_calls = {(f, d) for f, d in self.assigned_hall_calls if f != curr_f}
                if self.parking_target_floor == curr_f:
                    self.parking_target_floor = None

                # Choose next action
                next_target = self._select_next_target()
                if next_target is None:
                    # If empty but passengers are still queued at this floor, re-open doors immediately!
                    waiting_here = floor_queues.get(curr_f, [])
                    if waiting_here and len(self.passengers) < self.config.car_capacity:
                        self.state = ElevatorState.DOOR_OPEN
                        self.door_timer = self.config.door_operate_time
                    else:
                        self.state = ElevatorState.IDLE
                        self.direction = Direction.NONE
                else:
                    new_dir = Direction.UP if next_target > self.current_floor_pos else Direction.DOWN
                    if new_dir != self.direction:
                        self.reversal_count += 1
                    self.direction = new_dir
                    self.state = ElevatorState.ACCELERATING

        return exited_passengers

    def _move(self, dt: float):
        dist = self.velocity * dt
        self.total_travel_meters += dist
        floor_dist = dist / self.config.floor_height_meters
        if self.direction == Direction.UP:
            self.current_floor_pos = min(float(self.config.num_floors - 1), self.current_floor_pos + floor_dist)
        elif self.direction == Direction.DOWN:
            self.current_floor_pos = max(0.0, self.current_floor_pos - floor_dist)

    def _is_time_to_decelerate(self, target_floor: int) -> bool:
        """Calculates stopping distance d = v² / (2 * a)"""
        stopping_distance_meters = (self.velocity ** 2) / (2.0 * self.config.acceleration)
        current_distance_meters = abs(self.current_floor_pos - target_floor) * self.config.floor_height_meters
        return current_distance_meters <= (stopping_distance_meters + 0.3)

    def _get_next_stop_ahead(self) -> Optional[int]:
        targets = self.all_target_floors
        if not targets:
            return None

        if self.direction == Direction.UP:
            ahead = [f for f in targets if f >= self.current_floor_pos - 0.1]
            return min(ahead) if ahead else min(targets)
        elif self.direction == Direction.DOWN:
            ahead = [f for f in targets if f <= self.current_floor_pos + 0.1]
            return max(ahead) if ahead else max(targets)
        return self._select_next_target()

    def _select_next_target(self) -> Optional[int]:
        targets = self.all_target_floors
        if not targets:
            return None

        curr = self.current_floor_pos
        # Prefer continuing in current direction (LOOK heuristic)
        if self.direction == Direction.UP:
            ahead = [f for f in targets if f > curr + 0.05]
            if ahead:
                return min(ahead)
            behind = [f for f in targets if f < curr - 0.05]
            return max(behind) if behind else None
        elif self.direction == Direction.DOWN:
            ahead = [f for f in targets if f < curr - 0.05]
            if ahead:
                return max(ahead)
            behind = [f for f in targets if f > curr + 0.05]
            return min(behind) if behind else None
        else:
            # Nearest target
            return min(targets, key=lambda f: abs(f - curr))

    def _service_passengers(self, current_time: float, floor_queues: dict) -> Tuple[List[Passenger], List[Passenger]]:
        """Alights passengers at this floor and boards waiting queue."""
        curr_floor = self.current_floor_int
        exited: List[Passenger] = []
        remaining: List[Passenger] = []

        # 1. Alight passengers
        for p in self.passengers:
            if p.dest_floor == curr_floor:
                p.exit_time = current_time
                exited.append(p)
            else:
                remaining.append(p)
        self.passengers = remaining

        # Boundary checks & Empty car direction orientation
        if curr_floor == 0:
            self.direction = Direction.UP
        elif curr_floor == self.config.num_floors - 1:
            self.direction = Direction.DOWN
        elif len(self.passengers) == 0:
            self.direction = Direction.NONE

        # 2. Board passengers from floor queue
        boarded: List[Passenger] = []
        waiting = floor_queues.get(curr_floor, [])
        still_waiting = []

        # If car is empty and queue exists, align direction with waiting passengers
        if len(self.passengers) == 0 and waiting:
            self.direction = waiting[0].direction

        for p in waiting:
            space_left = len(self.passengers) < self.config.car_capacity
            # Match direction (or car has no set direction yet)
            dir_match = (p.direction == self.direction or self.direction == Direction.NONE)

            if space_left and dir_match:
                p.board_time = current_time
                p.assigned_elevator = self.car_id
                self.passengers.append(p)
                self.car_calls.add(p.dest_floor)
                boarded.append(p)
                self.direction = p.direction  # Lock in co-direction for remaining boarders
            else:
                still_waiting.append(p)

        floor_queues[curr_floor] = still_waiting
        return boarded, exited
