"""
Core Simulation Engine
Manages discrete-event loop, passenger lifecycles, elevator kinematics, and metrics telemetry.
"""

from typing import List, Dict, Type
from config import SimulationConfig, TrafficMode
from elevator import ElevatorCar
from passenger import Passenger, TrafficGenerator
from dispatcher import BaseDispatcher, HierarchicalMultiAgentDispatcher

class ElevatorSimulator:
    """Manages the full building simulation environment."""

    def __init__(self, config: SimulationConfig, dispatcher_cls: Type[BaseDispatcher] = HierarchicalMultiAgentDispatcher):
        self.config = config
        self.dispatcher: BaseDispatcher = dispatcher_cls(config)
        self.traffic_generator = TrafficGenerator(config)

        # Building State
        self.elevators: List[ElevatorCar] = [ElevatorCar(i, config) for i in range(config.num_elevators)]
        self.floor_queues: Dict[int, List[Passenger]] = {f: [] for f in range(config.num_floors)}

        # Simulation Time & Passenger Logs
        self.current_time: float = 0.0
        self.completed_passengers: List[Passenger] = []
        self.total_generated_count: int = 0

    def step(self, dt: float):
        """Advances the simulation by dt seconds."""
        self.current_time += dt

        # 1. Generate new passenger arrivals
        new_passengers = self.traffic_generator.generate_passengers(self.current_time, dt)
        for p in new_passengers:
            self.floor_queues[p.origin_floor].append(p)
            self.total_generated_count += 1

        # 2. Dispatcher assigns hall calls to elevator cars
        self.dispatcher.assign_calls(self.elevators, self.floor_queues, self.current_time, dt)

        # 3. Update each elevator car's kinematic FSM
        for car in self.elevators:
            exited = car.update(dt, self.current_time, self.floor_queues)
            self.completed_passengers.extend(exited)

    def run_headless(self, duration_seconds: float, dt: float = 0.5) -> dict:
        """Runs the simulation headless (without GUI) at high speed for benchmarking."""
        steps = int(duration_seconds / dt)
        for _ in range(steps):
            self.step(dt)
        return self.get_telemetry()

    def get_telemetry(self) -> dict:
        """Returns comprehensive real-time and aggregate metrics."""
        completed = self.completed_passengers
        awt = (sum(p.wait_time for p in completed) / len(completed)) if completed else 0.0
        ajt = (sum(p.journey_time for p in completed) / len(completed)) if completed else 0.0
        max_wait = max((p.wait_time for p in completed), default=0.0)

        # Also consider currently waiting passengers for live starvation monitoring
        live_waiting = [p for queue in self.floor_queues.values() for p in queue]
        current_max_wait = max(((self.current_time - p.call_time) for p in live_waiting), default=0.0)
        overall_max_wait = max(max_wait, current_max_wait)

        # Calculate Energy & Wear Index
        total_travel_meters = sum(c.total_travel_meters for c in self.elevators)
        total_door_cycles = sum(c.door_cycles for c in self.elevators)
        total_reversals = sum(c.reversal_count for c in self.elevators)

        energy_index = (
            self.config.energy_per_meter * total_travel_meters +
            self.config.energy_door_cycle * total_door_cycles +
            self.config.energy_reversal_cost * total_reversals
        )

        return {
            "dispatcher": self.dispatcher.name,
            "sim_time": self.current_time,
            "traffic_mode": self.config.traffic_mode.value,
            "total_generated": self.total_generated_count,
            "total_completed": len(completed),
            "active_waiting": len(live_waiting),
            "active_in_transit": sum(c.load_count for c in self.elevators),
            "awt": awt,
            "ajt": ajt,
            "max_wait_time": overall_max_wait,
            "total_travel_meters": total_travel_meters,
            "total_door_cycles": total_door_cycles,
            "total_reversals": total_reversals,
            "energy_index": energy_index
        }
