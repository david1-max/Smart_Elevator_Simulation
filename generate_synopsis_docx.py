import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=50, bottom=50, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.size = Pt(7.8)
    run.font.italic = True
    run.font.color.rgb = RGBColor(71, 85, 105)

def create_synopsis_doc(filename="PROJECT_SYNOPSIS.docx"):
    doc = docx.Document()
    
    # Page setup - Compact margins for tight 2-page fit
    for section in doc.sections:
        section.top_margin = Inches(0.4)
        section.bottom_margin = Inches(0.4)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        section.page_width = Inches(8.27)   # A4
        section.page_height = Inches(11.69) # A4

    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(8.8)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    normal_style.paragraph_format.line_spacing = 1.05
    normal_style.paragraph_format.space_after = Pt(2)

    # University & Department Header
    p_head = doc.add_paragraph()
    p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_head.paragraph_format.space_after = Pt(1)
    r_uni = p_head.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n")
    r_uni.bold = True
    r_uni.font.size = Pt(10.5)
    r_uni.font.color.rgb = RGBColor(15, 23, 42)
    
    r_sub = p_head.add_run("PROJECT SYNOPSIS — ACADEMIC CAPSTONE / MAJOR PROJECT\n")
    r_sub.bold = True
    r_sub.font.size = Pt(9)
    r_sub.font.color.rgb = RGBColor(37, 99, 235)

    # Project Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(3)
    r_title = p_title.add_run("Design and Simulation of a Hierarchical Multi-Agent AI System for Intelligent Group Elevator Dispatching in Multi-Zone High-Rise Buildings")
    r_title.bold = True
    r_title.font.size = Pt(11)
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    # Team & Supervisor Table Block
    meta_table = doc.add_table(rows=1, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    
    cell_l, cell_r = meta_table.rows[0].cells
    cell_l.width = Inches(3.9)
    cell_r.width = Inches(3.3)
    
    set_cell_background(cell_l, "F1F5F9")
    set_cell_background(cell_r, "F1F5F9")
    set_cell_margins(cell_l, top=40, bottom=40, left=80, right=80)
    set_cell_margins(cell_r, top=40, bottom=40, left=80, right=80)

    p_tl = cell_l.paragraphs[0]
    p_tl.paragraph_format.space_after = Pt(0)
    r = p_tl.add_run("Project Team Members:\n")
    r.bold = True
    r.font.size = Pt(8.2)
    r_members = p_tl.add_run(
        "• Divyanshu Yadav (Lead Researcher & System Architect)\n"
        "• Viraj & Co-developer (Core Algorithm & Simulation Engineering)\n"
        "• Vaibhav (Documentation, Technical Writing & Quality Assurance)"
    )
    r_members.font.size = Pt(8.0)

    p_tr = cell_r.paragraphs[0]
    p_tr.paragraph_format.space_after = Pt(0)
    r2 = p_tr.add_run("Supervision & Track:\n")
    r2.bold = True
    r2.font.size = Pt(8.2)
    r_sup = p_tr.add_run(
        "• Supervisor: [Faculty Guide / Dr. / Prof.]\n"
        "• Domain: Multi-Agent RL, Distributed Systems & Simulation\n"
        "• Platform: Python 3.10+, PyTorch, SimPy, Pygame"
    )
    r_sup.font.size = Pt(8.0)

    def add_sec_heading(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title_text)
        run.bold = True
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(30, 58, 138)
        return p

    # 1. INTRODUCTION & MOTIVATION
    add_sec_heading("1. INTRODUCTION & MOTIVATION")
    p1 = doc.add_paragraph()
    p1.add_run(
        "In modern multi-storey buildings, vertical transportation accounts for 5% to 15% of total building electrical energy and represents a critical bottleneck. Conventional Elevator Group Control Systems (EGCS) rely almost exclusively on static, deterministic dispatching heuristics (e.g., Nearest Car/ETA, Full Collective, or LOOK/SCAN). "
        "These rigid rules fail under non-stationary stochastic passenger surges—particularly morning Up-Peak, evening Down-Peak, and lunchtime Inter-Floor mobility. Crucially, static heuristics cause elevator bunching (cars shadowing one another along the same trajectory, starving other floors) and cannot anticipate demand under partial observability. "
        "This project develops an intelligent Group Elevator Controller utilizing a Hierarchical Multi-Agent System (H-MAS) combined with Multi-Agent Reinforcement Learning (MARL / MAPPO) and proactive idle parking to minimize passenger wait times, journey times, and empty car travel."
    )

    # 2. PROBLEM STATEMENT & FORMULATION
    add_sec_heading("2. PROBLEM STATEMENT & MATHEMATICAL FORMULATION")
    p2 = doc.add_paragraph()
    p2.add_run(
        "Given an N-floor building serviced by M independent elevator cars under a traditional Two-Button Hall-Call Interface (UP / DOWN):\n"
        "1. Partial Observability: When a passenger pushes the UP/DOWN button at floor i, the destination floor and passenger count remain strictly unknown until the elevator arrives and the passenger boards.\n"
        "2. Elevator Bunching Mitigation: Preventing trailing cars from following the leader and wasting energy on redundant stops.\n"
        "3. Multi-Objective Optimization: Formulated as min_π [ w1·AWT + w2·AJT + w3·StarvationPenalty + w4·EnergyIndex ], balancing waiting times, in-transit travel, starvation ceilings, and energy wear."
    )

    # 3. PROPOSED HIERARCHICAL MULTI-AGENT ARCHITECTURE (H-MAS)
    add_sec_heading("3. PROPOSED SYSTEM ARCHITECTURE (HIERARCHICAL MULTI-AGENT)")
    p3 = doc.add_paragraph()
    p3.add_run(
        "The project decouples global macro-allocation from local motion execution through a two-tier Hierarchical Multi-Agent framework:\n"
        "• Tier 1: Central Dispatcher Agent (Macro Level): Tracks global state tensor S_t (positions, velocities, load factors ρ_m = p_m/P_max, active hall call wait times). Uses MAPPO / Centralized Critic + ETA cost allocator with load-saturation penalty and proactive idle-car parking.\n"
        "• Tier 2: Autonomous Car Agents (Micro Level — M Cars): Operates a localized 7-State Kinematic FSM (IDLE → ACCEL → CRUISE → DECEL → DOOR_OPEN → SERVICING → DOOR_CLOSE), managing internal car calls, dynamic LOOK sweeps, and adaptive door dwell times."
    )

    # Insert Figure 1: Architecture
    if os.path.exists("architecture_h_mas.png"):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_before = Pt(3)
        p_img1.paragraph_format.space_after = Pt(1)
        run_img1 = p_img1.add_run()
        run_img1.add_picture("architecture_h_mas.png", width=Inches(6.6))
        add_caption(doc, "Figure 1: Hierarchical Multi-Agent Architecture (H-MAS) with Tier-1 Dispatcher and Tier-2 Autonomous Car Agents")

    # 4. HOW THE SYSTEM WORKS (OPERATIONAL LIFECYCLE)
    add_sec_heading("4. SYSTEM WORKFLOW: HOW ALL COMPONENTS WORK TOGETHER")
    
    # Insert Figure 2: Workflow Diagram
    if os.path.exists("architecture_workflow.png"):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(2)
        p_img2.paragraph_format.space_after = Pt(1)
        run_img2 = p_img2.add_run()
        run_img2.add_picture("architecture_workflow.png", width=Inches(6.4))
        add_caption(doc, "Figure 2: End-to-End Operational Lifecycle from Hall Call Generation to Boarding, Delivery, and Repositioning")

    # Insert Figure 3: FSM Diagram
    if os.path.exists("architecture_fsm.png"):
        p_img3 = doc.add_paragraph()
        p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img3.paragraph_format.space_before = Pt(2)
        p_img3.paragraph_format.space_after = Pt(1)
        run_img3 = p_img3.add_run()
        run_img3.add_picture("architecture_fsm.png", width=Inches(6.4))
        add_caption(doc, "Figure 3: Car Agent 7-State Kinematic Finite State Machine (FSM) Transition Model")

    # 5. TRAFFIC PROFILES & SIMULATION PLATFORM
    add_sec_heading("5. TRAFFIC PROFILES, PYGAME DASHBOARD & BENCHMARKING")
    p5 = doc.add_paragraph()
    p5.add_run(
        "• Traffic Profiles: Evaluates non-stationary Poisson arrivals across Up-Peak (80% lobby to upper), Down-Peak (80% upper to lobby), and Inter-Floor (uniform pairs) regimes.\n"
        "• Pygame 2D Graphical Dashboard: Real-time animated multi-shaft visualizer showing cabin coordinates, directional passenger queues, cabin load bars, and live streaming HUD telemetry (AWT, AJT, energy index). Parameter configurations allow dynamic scaling (N = 10 to 30+ floors, M = 2 to 8 cars).\n"
        "• Expected Targets vs. Baselines (LOOK/Collective): 20%-30% lower AWT, 15%-25% lower AJT, zero passenger starvation (<180s cap), and 15% lower energy wear."
    )

    # 6. ROADMAP & MILESTONES TABLE
    add_sec_heading("6. PROJECT IMPLEMENTATION ROADMAP & TEAM RESPONSIBILITIES")
    
    plan_table = doc.add_table(rows=5, cols=4)
    plan_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    plan_table.autofit = False
    
    headers = ["Phase", "Milestones / Deliverables", "Timeline", "Assigned Lead"]
    col_widths = [Inches(1.0), Inches(3.6), Inches(1.1), Inches(1.4)]
    
    for i, h in enumerate(headers):
        c = plan_table.rows[0].cells[i]
        c.width = col_widths[i]
        set_cell_background(c, "1E3A8A")
        set_cell_margins(c, top=30, bottom=30, left=50, right=50)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.8)
        r.font.color.rgb = RGBColor(255, 255, 255)

    timeline_data = [
        ("Phase 1", "Kinematic modeling, FSM state formulation, formal synopsis approval", "Weeks 1–2", "Divyanshu & Team"),
        ("Phase 2", "SimPy simulation engine, traffic Poisson generators, baseline heuristics", "Weeks 3–5", "Viraj & Co-dev"),
        ("Phase 3", "Tier-1 MARL Coordinator (MAPPO), Tier-2 FSM, and Proactive Parking Policy", "Weeks 6–8", "Divyanshu & Viraj"),
        ("Phase 4", "Pygame 2D interactive dashboard, live telemetry HUD, stress benchmarking", "Weeks 9–12", "Vaibhav & Team")
    ]

    for row_idx, data in enumerate(timeline_data, start=1):
        row = plan_table.rows[row_idx]
        bg = "FFFFFF" if row_idx % 2 != 0 else "F8FAFC"
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            cell.width = col_widths[col_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=25, bottom=25, left=50, right=50)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(7.6)
            if col_idx == 0:
                r.bold = True

    doc.save(filename)
    print(f"Document with 3 embedded architecture pictures successfully saved to {filename}")

if __name__ == "__main__":
    create_synopsis_doc()
