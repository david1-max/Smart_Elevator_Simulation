"""
Main Entry Point
Hierarchical Multi-Agent AI System for Group Elevator Dispatching in High-Rise Buildings
"""

import argparse
import sys
from config import SimulationConfig, TrafficMode
from simulator import ElevatorSimulator
from dispatcher import HierarchicalMultiAgentDispatcher
from benchmark import run_comparative_benchmark

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Elevator Dispatching Simulator")
    parser.add_argument("--mode", type=str, choices=["gui", "benchmark"], default="gui",
                        help="Run mode: 'gui' (Pygame Visualizer) or 'benchmark' (Headless batch test)")
    parser.add_argument("--floors", type=int, default=16, help="Number of building floors (default: 16)")
    parser.add_argument("--elevators", type=int, default=4, help="Number of elevator cars (default: 4)")
    parser.add_argument("--duration", type=float, default=240.0, help="Benchmark simulation duration in seconds")
    parser.add_argument("--traffic", type=str, choices=["up_peak", "down_peak", "inter_floor"], default="up_peak",
                        help="Initial traffic mode")

    args = parser.parse_args()

    # Map traffic arg
    traffic_map = {
        "up_peak": TrafficMode.UP_PEAK,
        "down_peak": TrafficMode.DOWN_PEAK,
        "inter_floor": TrafficMode.INTER_FLOOR
    }

    config = SimulationConfig(
        num_floors=args.floors,
        num_elevators=args.elevators,
        traffic_mode=traffic_map[args.traffic]
    )

    if args.mode == "benchmark":
        print(f"[*] Starting comparative benchmark for {args.floors} floors & {args.elevators} elevators...")
        run_comparative_benchmark(sim_duration=args.duration)
    else:
        # GUI mode
        try:
            from visualizer import PygameVisualizer
            sim = ElevatorSimulator(config, HierarchicalMultiAgentDispatcher)
            print(f"[*] Starting Pygame 2D Visual Dashboard ({args.floors} floors, {args.elevators} elevators)...")
            print("    Controls: [SPACE] Pause | [UP/DOWN] Speed | [D] Switch Algorithm | [T] Traffic Mode | [R] Reset")
            app = PygameVisualizer(sim)
            app.run()
        except ImportError as e:
            print(f"[!] Could not launch GUI: {e}")
            print("[*] Running headless benchmark instead...")
            run_comparative_benchmark(sim_duration=args.duration)

if __name__ == "__main__":
    main()
