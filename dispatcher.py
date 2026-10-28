"""
Group Elevator Dispatching Algorithms
Includes Baseline Dispatchers (Nearest Car, LOOK/Collective) and 
the Proposed Hierarchical Multi-Agent AI Dispatcher with Proactive Parking.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from config import Direction, ElevatorState, TrafficMode, SimulationConfig
from elevator import ElevatorCar
from passenger import Passenger

class BaseDispatcher(ABC):
    """Abstract Base Class for all Elevator Group Control System (EGCS) Dispatchers."""

    def __init__(self, config: SimulationConfig):
        self.config = config

    @abstractmethod
    def assign_calls(self, elevators: List[ElevatorCar], floor_queues: Dict[int, List[Passenger]], current_time: float, dt: float):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class NearestCarDispatcher(BaseDispatcher):
    """
    Baseline Heuristic: Nearest Car / Simple Estimated Time of Arrival (ETA).
    Greedily assigns each hall call to the car with the shortest distance, ignoring bunching.
    """

    @property
    def name(self) -> str:
        return "Nearest Car (Simple ETA Heuristic)"

    def assign_calls(self, elevators: List[ElevatorCar], floor_queues: Dict[int, List[Passenger]], current_time: float, dt: float):
        for floor, queue in floor_queues.items():
            if not queue:
                continue
            
            # Check active hall call directions needed on this floor
            dirs_needed = {p.direction for p in queue}
            for d in dirs_needed:
                # Find car with minimal distance
                best_car = min(
                    elevators,
                    key=lambda c: abs(c.current_floor_pos - floor)
                )
                best_car.assigned_hall_calls.add((floor, d))


class CollectiveLOOKDispatcher(BaseDispatcher):
    """
    Baseline Heuristic: Directional SCAN / Full Collective.
    Assigns calls to cars moving co-directionally towards the call.
    """

    @property
    def name(self) -> str:
        return "Directional LOOK / Full Collective"

    def assign_calls(self, elevators: List[ElevatorCar], floor_queues: Dict[int, List[Passenger]], current_time: float, dt: float):
        for floor, queue in floor_queues.items():
            if not queue:
                continue

            for d in {p.direction for p in queue}:
                best_car = None
                best_cost = 9999.0

                for car in elevators:
                    cost = abs(car.current_floor_pos - floor)
                    # Check co-directionality
                    if car.direction == Direction.UP:
                        if floor >= car.current_floor_pos and d == Direction.UP:
                            cost *= 1.0  # Favorable
                        else:
                            cost += self.config.num_floors * 2  # Needs full round-trip
                    elif car.direction == Direction.DOWN:
                        if floor <= car.current_floor_pos and d == Direction.DOWN:
                            cost *= 1.0  # Favorable
                        else:
                            cost += self.config.num_floors * 2
                    else: # IDLE
                        cost += 2.0

                    if cost < best_cost:
                        best_cost = cost
                        best_car = car

                if best_car:
                    best_car.assigned_hall_calls.add((floor, d))


class HierarchicalMultiAgentDispatcher(BaseDispatcher):
    """
    Proposed System: Tier-1 Global Coordinator Multi-Agent AI Dispatcher.
    Combines:
    1. Multi-factor state tensor evaluation (Proximity, Capacity Saturation, Heading).
    2. Dynamic Anti-Bunching Spacing Margin (prevents trailing elevators).
    3. Proactive Idle-Car Parking Policy (dispatches empty cars to predicted demand origins).
    """

    @property
    def name(self) -> str:
        return "Hierarchical Multi-Agent AI (H-MAS + Proactive Parking)"

    def assign_calls(self, elevators: List[ElevatorCar], floor_queues: Dict[int, List[Passenger]], current_time: float, dt: float):
        # 1. Capacity-Aware Multi-Agent Hall Call Allocation
        for floor, queue in floor_queues.items():
            if not queue:
                continue

            # Group calls by direction (UP / DOWN)
            calls_by_dir: Dict[Direction, List[Passenger]] = {}
            for p in queue:
                calls_by_dir.setdefault(p.direction, []).append(p)

            for direction, dir_passengers in calls_by_dir.items():
                pax_waiting = len(dir_passengers)

                # Calculate capacity already allocated to this floor & direction
                assigned_capacity = sum(
                    max(0, c.config.car_capacity - c.load_count)
                    for c in elevators
                    if (floor, direction) in c.assigned_hall_calls or (c.current_floor_int == floor and c.state in (ElevatorState.DOOR_OPEN, ElevatorState.SERVICING))
                )

                # If queue exceeds assigned capacity (e.g. lobby surge), dispatch multiple cars!
                while assigned_capacity < pax_waiting:
                    # Find candidate cars that are not yet full and not yet assigned to this stop
                    candidates = [c for c in elevators if not c.is_full and (floor, direction) not in c.assigned_hall_calls]
                    if not candidates:
                        break

                    best_car = min(
                        candidates,
                        key=lambda c: self._compute_agent_cost(c, floor, direction, elevators, pax_waiting)
                    )

                    best_car.assigned_hall_calls.add((floor, direction))
                    assigned_capacity += max(1, self.config.car_capacity - best_car.load_count)

        # 2. Proactive Parking Policy for Idle Cars
        self._execute_proactive_parking(elevators, floor_queues)

    def _compute_agent_cost(self, car: ElevatorCar, target_floor: int, call_dir: Direction, all_cars: List[ElevatorCar], passenger_count: int) -> float:
        """
        Calculates multi-objective assignment cost:
        Cost = TravelETA + LoadPenalty + ReversalPenalty + BunchingPenalty
        """
        N = self.config.num_floors
        dist_floors = abs(car.current_floor_pos - target_floor)

        # 1. Base Motion ETA
        eta_seconds = (dist_floors * self.config.floor_height_meters) / max(0.5, self.config.max_velocity)

        # 2. Directional Alignment
        is_toward = False
        if car.direction == Direction.UP and target_floor >= car.current_floor_pos and call_dir == Direction.UP:
            is_toward = True
        elif car.direction == Direction.DOWN and target_floor <= car.current_floor_pos and call_dir == Direction.DOWN:
            is_toward = True
        elif car.state == ElevatorState.IDLE:
            is_toward = True

        reversal_penalty = 0.0 if is_toward else 25.0

        # Intermediate stops penalty
        intermediate_stops = len([f for f in car.all_target_floors if min(car.current_floor_pos, target_floor) <= f <= max(car.current_floor_pos, target_floor)])
        stops_delay = intermediate_stops * (self.config.door_dwell_time + 2.0 * self.config.door_operate_time)

        # 3. Capacity Saturation Penalty (prevents overcrowding & bypassing)
        capacity_ratio = (car.load_count + passenger_count) / max(1, self.config.car_capacity)
        if capacity_ratio > 0.85:
            load_penalty = 40.0 * (capacity_ratio ** 2)
        else:
            load_penalty = 5.0 * capacity_ratio

        # 4. Anti-Bunching Penalty (Avoid shadowing a car right in front)
        bunching_penalty = 0.0
        for other in all_cars:
            if other.car_id != car.car_id and other.direction == car.direction and other.direction != Direction.NONE:
                gap = abs(other.current_floor_pos - car.current_floor_pos)
                if gap < 2.0: # Too close!
                    bunching_penalty += 30.0 / max(0.5, gap)

        return eta_seconds + stops_delay + reversal_penalty + load_penalty + bunching_penalty

    def _execute_proactive_parking(self, elevators: List[ElevatorCar], floor_queues: Dict[int, List[Passenger]]):
        """Reposition idle cars to predicted high-traffic zones before calls arrive."""
        mode = self.config.traffic_mode
        N = self.config.num_floors
        idle_cars = [c for c in elevators if c.state == ElevatorState.IDLE and not c.all_target_floors]

        if not idle_cars:
            return

        lobby_queue_len = len(floor_queues.get(0, []))

        # If lobby has a surge (or Up-Peak mode), mobilize idle cars to Ground immediately!
        if mode == TrafficMode.UP_PEAK or lobby_queue_len > 0:
            for c in idle_cars:
                if c.current_floor_int != 0 and c.parking_target_floor is None:
                    c.parking_target_floor = 0
            return

        if mode == TrafficMode.DOWN_PEAK:
            # Stage idle cars in upper half of building
            upper_floors = [int(N * 0.75), int(N * 0.50), int(N * 0.85)]
            for c, target_f in zip(idle_cars, upper_floors):
                if c.parking_target_floor is None and abs(c.current_floor_int - target_f) > 2:
                    c.parking_target_floor = target_f

        elif mode == TrafficMode.INTER_FLOOR:
            # Balanced zoning (spread cars evenly across building height)
            ideal_zones = [int(N * (i + 1) / (len(elevators) + 1)) for i in range(len(elevators))]
            for c, target_f in zip(idle_cars, ideal_zones):
                if c.parking_target_floor is None and abs(c.current_floor_int - target_f) > 3:
                    c.parking_target_floor = target_f
