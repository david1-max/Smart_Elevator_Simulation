import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

def create_system_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background canvas
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    # Main Title
    ax.text(50, 96.5, "HIERARCHICAL MULTI-AGENT ARCHITECTURE (H-MAS)", 
            fontsize=15, fontweight='bold', ha='center', va='center', color='#0F172A')
    ax.text(50, 93.5, "Decoupled Macro Call Dispatching & Autonomous Micro Kinematics", 
            fontsize=9.5, ha='center', va='center', color='#475569', style='italic')

    # ==================== TIER 1: GLOBAL DISPATCHER ====================
    tier1_bg = FancyBboxPatch((4, 57), 92, 33, boxstyle="round,pad=0.5,rounding_size=1.5",
                              ec="#1E3A8A", fc="#EFF6FF", lw=2, zorder=1)
    ax.add_patch(tier1_bg)

    ax.text(7, 87, "TIER 1: CENTRAL DISPATCHER & FLOOR COORDINATOR (Global Level)", 
            fontsize=11.5, fontweight='bold', color='#1E3A8A', zorder=2)
    ax.text(7, 84.2, "Centralized Critic & Multi-Agent Reinforcement Learning (MAPPO) / ETA Allocator", 
            fontsize=8.5, color='#3B82F6', fontweight='semibold', zorder=2)

    # Box 1.1: State Tensor
    b1 = FancyBboxPatch((7, 61), 26, 20, boxstyle="round,pad=0.4,rounding_size=1",
                         ec="#93C5FD", fc="#FFFFFF", lw=1.5, zorder=2)
    ax.add_patch(b1)
    ax.text(20, 78.5, "GLOBAL STATE TENSOR (St)", fontsize=9, fontweight='bold', ha='center', color='#1E40AF', zorder=3)
    ax.plot([8.5, 31.5], [76.5, 76.5], color='#DBEAFE', lw=1.2, zorder=3)
    s_lines = [
        "• Hall Calls: [Floor i, Dir {▲, ▼}]",
        "• Queue Elapsed Wait Times (AWT)",
        "• Fleet Positions: [f1, f2, ... fM]",
        "• Velocity Vectors: [v1, v2, ... vM]",
        "• Cabin Load Factors: ρm = pm/Pmax",
        "• Active Traffic Regime Tracker"
    ]
    for idx, line in enumerate(s_lines):
        ax.text(9, 74 - idx*2.5, line, fontsize=7.5, color='#334155', zorder=3)

    # Box 1.2: Decision Policy Core
    b2 = FancyBboxPatch((36.5, 61), 27, 20, boxstyle="round,pad=0.4,rounding_size=1",
                         ec="#3B82F6", fc="#FFFFFF", lw=1.5, zorder=2)
    ax.add_patch(b2)
    ax.text(50, 78.5, "DISPATCH POLICY ENGINE", fontsize=9, fontweight='bold', ha='center', color='#1E40AF', zorder=3)
    ax.plot([38, 62], [76.5, 76.5], color='#DBEAFE', lw=1.2, zorder=3)
    d_lines = [
        "• Deep Q-Network / Central Actor",
        "• Dynamic ETA Cost Optimization",
        "• Load Saturation Penalty (ρm > 0.85)",
        "• Directional Reversal Penalty",
        "• Anti-Bunching Spacing Margin",
        "• Hall Call -> Optimal Car ID (C*)"
    ]
    for idx, line in enumerate(d_lines):
        ax.text(38.5, 74 - idx*2.5, line, fontsize=7.5, color='#334155', zorder=3)

    # Box 1.3: Proactive Parking
    b3 = FancyBboxPatch((66.5, 61), 26.5, 20, boxstyle="round,pad=0.4,rounding_size=1",
                         ec="#93C5FD", fc="#FFFFFF", lw=1.5, zorder=2)
    ax.add_patch(b3)
    ax.text(79.7, 78.5, "PROACTIVE PARKING AGENT", fontsize=9, fontweight='bold', ha='center', color='#1E40AF', zorder=3)
    ax.plot([68, 91.5], [76.5, 76.5], color='#DBEAFE', lw=1.2, zorder=3)
    p_lines = [
        "• Historical Demand Profiler",
        "• Up-Peak: Reposition to Lobby",
        "• Down-Peak: Reposition Upper Floors",
        "• Inter-Floor: Zone Decentralization",
        "• Idle Car Reposition Commands",
        "• Minimizes Future Pickup Latency"
    ]
    for idx, line in enumerate(p_lines):
        ax.text(68.5, 74 - idx*2.5, line, fontsize=7.5, color='#334155', zorder=3)

    # ==================== INTER-TIER COMMUNICATION BUS ====================
    # Downward Dispatch Arrow
    ax.annotate("", xy=(30, 48.5), xytext=(30, 57),
                arrowprops=dict(arrowstyle="-|>", color="#2563EB", lw=2.5, mutation_scale=15), zorder=4)
    ax.text(31.5, 52.8, "Hall Call Assignments (Target Floor, Car ID)", 
            fontsize=8.2, fontweight='bold', color="#1D4ED8", va='center', zorder=4)

    # Upward Telemetry Arrow
    ax.annotate("", xy=(70, 57), xytext=(70, 48.5),
                arrowprops=dict(arrowstyle="-|>", color="#059669", lw=2.5, mutation_scale=15), zorder=4)
    ax.text(71.5, 52.8, "Real-time Telemetry (Position, Velocity, Load, FSM State)", 
            fontsize=8.2, fontweight='bold', color="#047857", va='center', zorder=4)

    # ==================== TIER 2: LOCAL CAR AGENTS ====================
    tier2_bg = FancyBboxPatch((4, 4), 92, 44, boxstyle="round,pad=0.5,rounding_size=1.5",
                              ec="#047857", fc="#F0FDF4", lw=2, zorder=1)
    ax.add_patch(tier2_bg)

    ax.text(7, 44.5, "TIER 2: AUTONOMOUS CAR AGENTS (Micro Kinematic Level - M Parallel Cabs)", 
            fontsize=11.5, fontweight='bold', color='#047857', zorder=2)
    ax.text(7, 42, "Decentralized Execution: Local Kinematic FSM, Passenger Safety, & Adaptive Door Control", 
            fontsize=8.5, color='#059669', fontweight='semibold', zorder=2)

    car_boxes = [
        (7, "CAR AGENT 1 (Cab 1)", "#10B981", [
            "• Assigned Hall Calls Queue",
            "• Internal Destination Calls",
            "• 7-State Kinematic FSM",
            "• Dynamic LOOK Sweep",
            "• Adaptive Dwell Timer",
            "• Real-time Weight Sensor"
        ]),
        (38, "CAR AGENT 2 (Cab 2)", "#10B981", [
            "• Assigned Hall Calls Queue",
            "• Internal Destination Calls",
            "• 7-State Kinematic FSM",
            "• Dynamic LOOK Sweep",
            "• Adaptive Dwell Timer",
            "• Real-time Weight Sensor"
        ]),
        (69, "CAR AGENT M (Cab M)", "#10B981", [
            "• Assigned Hall Calls Queue",
            "• Internal Destination Calls",
            "• 7-State Kinematic FSM",
            "• Dynamic LOOK Sweep",
            "• Adaptive Dwell Timer",
            "• Real-time Weight Sensor"
        ])
    ]

    for x_pos, title, border_col, details in car_boxes:
        c_box = FancyBboxPatch((x_pos, 7.5), 24, 32.5, boxstyle="round,pad=0.4,rounding_size=1",
                               ec=border_col, fc="#FFFFFF", lw=1.5, zorder=2)
        ax.add_patch(c_box)
        ax.text(x_pos + 12, 37.5, title, fontsize=8.8, fontweight='bold', ha='center', color='#065F46', zorder=3)
        ax.plot([x_pos + 1.5, x_pos + 22.5], [35.5, 35.5], color='#A7F3D0', lw=1.2, zorder=3)
        
        for idx, line in enumerate(details):
            ax.text(x_pos + 1.5, 32.5 - idx*3.5, line, fontsize=7.5, color='#334155', zorder=3)
            
        # Small visual indicator of elevator
        rect_cab = patches.Rectangle((x_pos + 7.5, 9.5), 9, 3.5, ec="#059669", fc="#D1FAE5", lw=1.2, zorder=3)
        ax.add_patch(rect_cab)
        ax.text(x_pos + 12, 11.2, "CAB PHYSICAL UNIT", fontsize=6.2, ha='center', va='center', fontweight='bold', color="#065F46", zorder=4)

    # Ellipsis for intermediate cars
    ax.text(65.5, 23, "• • •", fontsize=14, fontweight='bold', color='#64748B', ha='center', zorder=3)

    plt.tight_layout()
    plt.savefig("architecture_h_mas.png", dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print("architecture_h_mas.png generated successfully.")

def create_fsm_diagram():
    fig, ax = plt.subplots(figsize=(12, 6.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    # Title
    ax.text(50, 95.5, "LOCAL CAR AGENT: 7-STATE KINEMATIC FINITE STATE MACHINE (FSM)", 
            fontsize=14, fontweight='bold', ha='center', va='center', color='#0F172A')
    ax.text(50, 92, "Governing Micro-Motion, Passenger Safety Interlocks, and Dwell Cycles", 
            fontsize=9.2, ha='center', va='center', color='#475569', style='italic')

    # State Box Coordinates & Colors
    # Layout: Loop flow
    # IDLE (top left) -> ACCEL -> CRUISE -> DECEL -> STOP/DOOR_OPEN -> SERVICING -> DOOR_CLOSE -> IDLE or Next Stop
    states = [
        ("IDLE", 14, 73, "#64748B", "#F1F5F9", "Awaiting Hall/Car calls;\nproactive parking ready"),
        ("ACCELERATING", 50, 73, "#D97706", "#FEF3C7", "Ramp-up velocity;\na = 1.0 m/s²"),
        ("CRUISE", 86, 73, "#2563EB", "#DBEAFE", "Constant velocity;\nv_max = 2.5 m/s"),
        ("DECELERATING", 86, 25, "#DC2626", "#FEE2E2", "Approaching target floor;\na = -1.0 m/s²"),
        ("DOOR_OPEN", 50, 25, "#7C3AED", "#EDE9FE", "Interlock check;\nopening door curtains"),
        ("SERVICING", 14, 25, "#059669", "#D1FAE5", "Boarding/Alighting;\nadaptive dwell timer"),
        ("DOOR_CLOSE", 14, 49, "#475569", "#E2E8F0", "Safety curtain clear;\nclosing doors")
    ]

    for name, x, y, border_c, bg_c, desc in states:
        box = FancyBboxPatch((x - 10, y - 9), 20, 18, boxstyle="round,pad=0.4,rounding_size=1.2",
                             ec=border_c, fc=bg_c, lw=2, zorder=2)
        ax.add_patch(box)
        ax.text(x, y + 4.2, name, fontsize=8.8, fontweight='bold', ha='center', va='center', color=border_c, zorder=3)
        ax.plot([x - 8, x + 8], [y + 0.8, y + 0.8], color=border_c, lw=1, alpha=0.5, zorder=3)
        ax.text(x, y - 4, desc, fontsize=6.8, ha='center', va='center', color='#334155', zorder=3)

    # Transition Arrows
    def draw_arrow(x1, y1, x2, y2, label="", lbl_pos=(0, 0), color="#1E293B", rad=0.0):
        connection = f"arc3,rad={rad}" if rad != 0.0 else "arc3,rad=0"
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2, mutation_scale=14, connectionstyle=connection),
                    zorder=4)
        if label:
            ax.text(lbl_pos[0], lbl_pos[1], label, fontsize=7.2, fontweight='semibold',
                    ha='center', va='center', color=color,
                    bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec=color, lw=0.8, alpha=0.9), zorder=5)

    # IDLE -> ACCEL
    draw_arrow(24, 73, 40, 73, "Call Dispatched", (32, 76.5), color="#D97706")
    # ACCEL -> CRUISE
    draw_arrow(60, 73, 76, 73, "v reaches v_max", (68, 76.5), color="#2563EB")
    # CRUISE -> DECEL
    draw_arrow(86, 64, 86, 34, "Target Floor Proximity", (86, 49), color="#DC2626")
    # DECEL -> DOOR_OPEN
    draw_arrow(76, 25, 60, 25, "v = 0 (Floor Aligned)", (68, 21.5), color="#7C3AED")
    # DOOR_OPEN -> SERVICING
    draw_arrow(40, 25, 24, 25, "Doors fully open", (32, 21.5), color="#059669")
    # SERVICING -> DOOR_CLOSE
    draw_arrow(14, 34, 14, 40, "Dwell timer elapsed\n& safety beam clear", (14, 37), color="#475569")
    # DOOR_CLOSE -> IDLE (No calls left)
    draw_arrow(14, 58, 14, 64, "No further calls\n(Queue Empty)", (14, 61), color="#64748B")
    # DOOR_CLOSE -> ACCEL (Further calls in queue)
    draw_arrow(24, 49, 44, 65, "Pending co-directional calls", (34, 55), color="#D97706", rad=-0.15)

    plt.tight_layout()
    plt.savefig("architecture_fsm.png", dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print("architecture_fsm.png generated successfully.")

def create_workflow_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(50, 96, "END-TO-END OPERATIONAL LIFECYCLE & DISPATCH WORKFLOW", 
            fontsize=14, fontweight='bold', ha='center', va='center', color='#0F172A')
    ax.text(50, 92.5, "From Hall-Call Generation to Passenger Delivery and Proactive Repositioning", 
            fontsize=9.2, ha='center', va='center', color='#475569', style='italic')

    steps = [
        (1, "1. PASSENGER ARRIVAL & HALL CALL", 18, 77, "#2563EB", [
            "• Passenger arrives at Floor i",
            "• Presses UP (▲) or DOWN (▼)",
            "• Event logged: (fi, di, t_call)",
            "• Destination remains UNKNOWN"
        ]),
        (2, "2. GLOBAL TENSOR EVALUATION", 50, 77, "#7C3AED", [
            "• Tier 1 reads building State St",
            "• Scans car locations, loads, queues",
            "• Evaluates MAPPO value Q(St, a)",
            "• Computes augmented ETA scores"
        ]),
        (3, "3. CAR ASSIGNMENT & DISPATCH", 82, 77, "#059669", [
            "• Optimal car selected (Car m)",
            "• Load balance penalty checked",
            "• Anti-bunching dwell adjusted",
            "• Stop injected into Car m queue"
        ]),
        (4, "4. KINEMATIC MOTION & ARRIVAL", 82, 28, "#D97706", [
            "• Car m FSM initiates motion",
            "• ACCEL -> CRUISE -> DECEL",
            "• Levels precisely with Floor i",
            "• DOOR_OPEN interlock engaged"
        ]),
        (5, "5. BOARDING & DESTINATION REVEAL", 50, 28, "#0284C7", [
            "• Passenger boards the elevator",
            "• Wait Time logged: AWT = t_board - t_call",
            "• Passenger selects destination inside car",
            "• Partial -> Full information revealed"
        ]),
        (6, "6. TRANSIT, EXIT & REPOSITIONING", 18, 28, "#475569", [
            "• Car travels to passenger destination",
            "• Passenger exits; Journey Time (AJT) logged",
            "• If queue empty -> Car enters IDLE",
            "• Proactive parking repositions empty car"
        ])
    ]

    for num, title, x, y, color, points in steps:
        box = FancyBboxPatch((x - 14, y - 13), 28, 26, boxstyle="round,pad=0.4,rounding_size=1.2",
                             ec=color, fc="#FFFFFF", lw=1.8, zorder=2)
        ax.add_patch(box)
        
        # Header strip
        strip = FancyBboxPatch((x - 14, y + 8), 28, 5, boxstyle="round,pad=0.2,rounding_size=0.6",
                               ec=color, fc=color, lw=1, zorder=3)
        ax.add_patch(strip)
        ax.text(x, y + 10.5, title, fontsize=7.8, fontweight='bold', ha='center', va='center', color="#FFFFFF", zorder=4)

        for idx, pt in enumerate(points):
            ax.text(x - 12, y + 4 - idx*3.6, pt, fontsize=7.4, color="#334155", zorder=3)

    # Workflow arrows
    def draw_wf_arrow(x1, y1, x2, y2, color="#2563EB", rad=0.0):
        connection = f"arc3,rad={rad}" if rad != 0.0 else "arc3,rad=0"
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2.5, mutation_scale=16, connectionstyle=connection),
                    zorder=4)

    # 1 -> 2
    draw_wf_arrow(32, 77, 36, 77, color="#2563EB")
    # 2 -> 3
    draw_wf_arrow(64, 77, 68, 77, color="#7C3AED")
    # 3 -> 4
    draw_wf_arrow(82, 64, 82, 41, color="#059669")
    # 4 -> 5
    draw_wf_arrow(68, 28, 64, 28, color="#D97706")
    # 5 -> 6
    draw_wf_arrow(36, 28, 32, 28, color="#0284C7")
    # 6 -> Proactive loop back to 1
    draw_wf_arrow(18, 41, 18, 64, color="#475569")
    ax.text(14, 52.5, "Proactive Repositioning Cycle", fontsize=7.2, fontweight='bold',
            color="#475569", ha='center', va='center', rotation=90,
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#475569", lw=0.8), zorder=5)

    plt.tight_layout()
    plt.savefig("architecture_workflow.png", dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print("architecture_workflow.png generated successfully.")

if __name__ == "__main__":
    create_system_architecture_diagram()
    create_fsm_diagram()
    create_workflow_diagram()
