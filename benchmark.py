"""
Automated Benchmarking Suite
Compares Nearest Car (ETA), LOOK/Collective, and Hierarchical Multi-Agent AI (H-MAS)
across identical random traffic seeds and outputs comparative metrics & plots.
"""

import copy
import random
import json
import matplotlib.pyplot as plt
import numpy as np
from config import SimulationConfig, TrafficMode
from simulator import ElevatorSimulator
from dispatcher import NearestCarDispatcher, CollectiveLOOKDispatcher, HierarchicalMultiAgentDispatcher

def run_comparative_benchmark(sim_duration: float = 300.0, seed: int = 42):
    """Runs all 3 dispatchers under the exact same traffic conditions."""
    print(f"\n====================================================================")
    print(f"RUNNING COMPARATIVE BENCHMARK (Duration: {sim_duration}s, Seed: {seed})")
    print(f"====================================================================\n")

    dispatchers = [
        ("Nearest Car (ETA)", NearestCarDispatcher),
        ("LOOK / Collective", CollectiveLOOKDispatcher),
        ("Hierarchical Multi-Agent (H-MAS)", HierarchicalMultiAgentDispatcher)
    ]

    results = []

    for name, disp_cls in dispatchers:
        # Reset random seed for identical traffic generation
        random.seed(seed)
        config = SimulationConfig(
            num_floors=16,
            num_elevators=4,
            traffic_mode=TrafficMode.UP_PEAK,
            arrival_rate_lambda=0.5
        )
        sim = ElevatorSimulator(config, disp_cls)
        print(f"[*] Simulating: {name} ...")
        metrics = sim.run_headless(duration_seconds=sim_duration, dt=0.5)
        results.append(metrics)
        print(f"    -> Completed: {metrics['total_completed']} passengers | AWT: {metrics['awt']:.1f}s | Energy: {metrics['energy_index']:.1f}")

    # Generate Comparative Bar Chart
    labels = [r["dispatcher"] for r in results]
    awts = [r["awt"] for r in results]
    ajts = [r["ajt"] for r in results]
    max_waits = [r["max_wait_time"] for r in results]
    energies = [r["energy_index"] for r in results]

    # Print Table
    print("\n" + "=" * 80)
    print(f"{'DISPATCHER ALGORITHM':<38} | {'AWT (s)':<9} | {'AJT (s)':<9} | {'MAX WAIT':<10} | {'ENERGY':<8}")
    print("-" * 80)
    for r in results:
        disp_short = r['dispatcher'].split('(')[0].strip()
        print(f"{disp_short:<38} | {r['awt']:<9.1f} | {r['ajt']:<9.1f} | {r['max_wait_time']:<10.1f} | {r['energy_index']:<8.0f}")
    print("=" * 80 + "\n")

    # Plotting comparison chart
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)
    fig.patch.set_facecolor('#F8FAFC')
    short_names = ["Nearest Car", "LOOK / Coll.", "H-MAS (AI)"]
    colors = ['#EF4444', '#F59E0B', '#10B981']

    # 1. AWT & AJT
    x = np.arange(len(short_names))
    width = 0.35
    axes[0].bar(x - width/2, awts, width, label='Wait Time (AWT)', color='#3B82F6', edgecolor='#1E40AF')
    axes[0].bar(x + width/2, ajts, width, label='Journey Time (AJT)', color='#10B981', edgecolor='#065F46')
    axes[0].set_title("Passenger Latency (s) [Lower is Better]", fontweight='bold', fontsize=11, color='#0F172A')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(short_names, fontweight='semibold')
    axes[0].legend(frameon=True, facecolor='#FFFFFF')
    axes[0].grid(axis='y', linestyle='--', alpha=0.5)

    # 2. Maximum Wait Time (Anti-Starvation)
    bars2 = axes[1].bar(short_names, max_waits, color=colors, edgecolor='#0F172A', width=0.5)
    axes[1].set_title("Maximum Passenger Wait Time (s)", fontweight='bold', fontsize=11, color='#0F172A')
    axes[1].grid(axis='y', linestyle='--', alpha=0.5)
    for bar in bars2:
        yval = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}s", ha='center', va='bottom', fontsize=9, fontweight='bold')

    # 3. Energy & Wear Index
    bars3 = axes[2].bar(short_names, energies, color=['#94A3B8', '#94A3B8', '#3B82F6'], edgecolor='#0F172A', width=0.5)
    axes[2].set_title("Energy & Wear Index [Lower is Better]", fontweight='bold', fontsize=11, color='#0F172A')
    axes[2].grid(axis='y', linestyle='--', alpha=0.5)
    for bar in bars3:
        yval = bar.get_height()
        axes[2].text(bar.get_x() + bar.get_width()/2, yval + 15, f"{int(yval)}", ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.suptitle("BENCHMARK COMPARISON: AI DISPATCHER VS. CONVENTIONAL BASELINES", fontsize=13, fontweight='bold', color='#1E3A8A', y=1.02)
    plt.tight_layout()
    chart_file = "benchmark_comparison.png"
    plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] Benchmark comparison chart saved to: {chart_file}")

    # Save to JSON
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"[OK] Benchmark data exported to: benchmark_results.json")

    return results

if __name__ == "__main__":
    run_comparative_benchmark(sim_duration=240.0)
