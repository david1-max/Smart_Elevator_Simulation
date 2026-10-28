# Hierarchical Multi-Agent AI System for Intelligent Group Elevator Dispatching

> **Capstone Project — Department of Computer Science & Engineering**  
> **Team:** Divyanshu Yadav, Viraj, Vaibhav

---

## 📌 Project Overview
This project designs and simulates an intelligent **Hierarchical Multi-Agent System (H-MAS)** for Elevator Group Control Systems (EGCS) in multi-zone high-rise buildings. 

It decouples macro-level call dispatching from micro-level elevator kinematics:
* **Tier 1 (Global Coordinator):** Evaluates building state tensors, optimizes multi-factor ETA and load saturation, suppresses elevator bunching, and executes a **Proactive Idle-Car Parking Policy**.
* **Tier 2 (Autonomous Car Agents):** 7-State Kinematic Finite State Machine (`IDLE` &rarr; `ACCEL` &rarr; `CRUISE` &rarr; `DECEL` &rarr; `DOOR_OPEN` &rarr; `SERVICING` &rarr; `DOOR_CLOSE`).

---

## 🗂️ Project Architecture & Files

```
├── config.py              # System geometry, speed curves, physical constants & traffic settings
├── passenger.py           # Passenger dataclass & stochastic Poisson arrival generators
├── elevator.py            # Car Agent with 7-State Kinematic FSM & passenger boarding logic
├── dispatcher.py          # Nearest Car (ETA), Directional LOOK, and H-MAS AI Dispatcher
├── simulator.py           # Discrete-event simulation loop and telemetry logger
├── visualizer.py          # Interactive 2D Pygame Graphical Dashboard & HUD
├── benchmark.py           # Automated comparative benchmark suite & Matplotlib chart generator
├── main.py                # CLI launch point for GUI and Benchmarks
├── PROJECT_SYNOPSIS.docx  # 2-Page formatted academic submission document (Microsoft Word)
├── PROJECT_SYNOPSIS.html  # 2-Page printable HTML format (1-click PDF export)
├── PROJECT_SYNOPSIS.md    # Complete academic synopsis specification
└── PROJECT_SYNOPSIS.tex   # Camera-ready IEEE 2-Column LaTeX template
```

---

## 🚀 How to Run the Project

### 1. Launch the 2D Interactive Graphical Visualizer (Pygame)
To start the live elevator simulation with the graphical dashboard:
```powershell
python main.py
```

#### **Interactive Controls during Simulation:**
* **`[SPACE]`**: Pause / Resume simulation
* **`[UP / DOWN ARROW]`**: Speed up or slow down ($0.5\times \dots 10.0\times$)
* **`[D]`**: Live toggle between dispatching algorithms:
  * `Hierarchical Multi-Agent AI (H-MAS)`
  * `Directional LOOK / Full Collective`
  * `Nearest Car (Simple ETA)`
* **`[T]`**: Live cycle between traffic profiles:
  * `Up-Peak` (Morning Lobby Surge)
  * `Down-Peak` (Evening Ground Egress)
  * `Inter-Floor` (Balanced / Lunchtime)
* **`[R]`**: Reset simulation

### 2. Customize Building Height and Fleet Size
```powershell
# Run a 24-floor tower with 6 elevators:
python main.py --floors 24 --elevators 6
```

### 3. Run the Automated Headless Benchmark
To run high-speed comparative testing across all dispatchers and generate comparison charts:
```powershell
python main.py --mode benchmark --duration 240
```
This generates:
* `benchmark_comparison.png` (Comparison bar charts of AWT, Max Wait Time, and Energy)
* `benchmark_results.json` (Raw statistical metrics)
