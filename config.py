"""
Elevator Group Control System (EGCS) - Configuration Parameters
Hierarchical Multi-Agent AI System for High-Rise Buildings
"""

from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = -1
    NONE = 0

class ElevatorState(Enum):
    IDLE = 0
    ACCELERATING = 1
    CRUISE = 2
    DECELERATING = 3
    DOOR_OPEN = 4
    SERVICING = 5
    DOOR_CLOSE = 6

class TrafficMode(Enum):
    UP_PEAK = "Up-Peak (Morning Lobby Surge)"
    DOWN_PEAK = "Down-Peak (Evening Exit Surge)"
    INTER_FLOOR = "Inter-Floor (Lunchtime / Balanced)"

@dataclass
class SimulationConfig:
    # Building Geometry
    num_floors: int = 16
    num_elevators: int = 4
    floor_height_meters: float = 3.5  # meters per floor

    # Elevator Kinematics & Physical Constraints
    max_velocity: float = 2.5         # m/s
    acceleration: float = 1.0         # m/s²
    door_operate_time: float = 1.5    # seconds to open or close
    door_dwell_time: float = 2.5      # base boarding wait time in seconds
    passenger_transfer_time: float = 0.8  # seconds per boarding/alighting passenger
    car_capacity: int = 10            # max passengers per cabin

    # Traffic Generation Parameters
    traffic_mode: TrafficMode = TrafficMode.UP_PEAK
    arrival_rate_lambda: float = 0.6  # passengers per second globally

    # Energy Consumption Weights
    energy_per_meter: float = 2.0     # kWh or arbitrary energy unit per meter moved
    energy_door_cycle: float = 1.5    # energy per door cycle
    energy_reversal_cost: float = 3.0 # wear penalty per directional change

    # Display / GUI Settings
    screen_width: int = 1200
    screen_height: int = 750
    fps: int = 60
    sim_speed: float = 2.0            # simulation acceleration multiplier
