"""
Pygame 2D Interactive Graphical Visualizer & Telemetry HUD
Dynamically partitioned layout ensuring 100% visibility of all elevator shafts,
moving cabs, floor queues, and the telemetry dashboard with zero overlap.
"""

import sys
import pygame
from typing import List
from config import SimulationConfig, Direction, ElevatorState, TrafficMode
from simulator import ElevatorSimulator
from dispatcher import HierarchicalMultiAgentDispatcher, CollectiveLOOKDispatcher, NearestCarDispatcher

class PygameVisualizer:
    """Real-Time 2D Graphical Dashboard for the Elevator Group Control System."""

    def __init__(self, simulator: ElevatorSimulator):
        self.sim = simulator
        self.config = simulator.config

        # Initialize Pygame
        pygame.init()
        pygame.font.init()

        # Window Dimensions (Adaptive & Resizable)
        self.width = max(1150, self.config.screen_width)
        self.height = max(720, self.config.screen_height)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Hierarchical Multi-Agent AI - Group Elevator Dispatching Simulator")
        self.clock = pygame.time.Clock()

        # Fonts
        self.title_font = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.header_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.font = pygame.font.SysFont("Segoe UI", 10)
        self.small_font = pygame.font.SysFont("Segoe UI", 9)
        self.bold_small = pygame.font.SysFont("Segoe UI", 9, bold=True)

        # Simulation Speed & State
        self.paused = False
        self.speed_multiplier = 2.0
        self.dispatchers = [
            HierarchicalMultiAgentDispatcher,
            CollectiveLOOKDispatcher,
            NearestCarDispatcher
        ]
        self.current_disp_idx = 0

        # Calculate Layout
        self._update_layout_geometry()

    def _update_layout_geometry(self):
        """Calculates non-overlapping coordinate spaces for Building and HUD."""
        # Right Column: Telemetry HUD
        self.hud_width = 330
        self.hud_x = self.width - self.hud_width - 15
        self.header_height = 55
        self.building_top = self.header_height + 15
        self.building_bottom = self.height - 20

        # Left Column: High-Rise Building Area
        self.building_left = 45
        # Ensure building stops strictly 25px before the HUD starts
        self.building_right = self.hud_x - 25
        self.building_width = max(300, self.building_right - self.building_left)

        # Vertical floor spacing
        self.floor_height_px = (self.building_bottom - self.building_top) / self.config.num_floors

        # Horizontal partitioning inside building
        self.queue_area_width = 85  # Floor labels and UP/DOWN queue badges
        self.shaft_area_x = self.building_left + self.queue_area_width + 10
        self.shaft_area_width = self.building_right - self.shaft_area_x - 15

        # Slot per elevator
        M = max(1, self.config.num_elevators)
        self.slot_width = self.shaft_area_width / M

    def run(self):
        running = True
        dt_frame = 1.0 / self.config.fps

        while running:
            # Handle Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.width = max(1000, event.w)
                    self.height = max(650, event.h)
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self._update_layout_geometry()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_UP:
                        self.speed_multiplier = min(10.0, self.speed_multiplier + 1.0)
                    elif event.key == pygame.K_DOWN:
                        self.speed_multiplier = max(0.5, self.speed_multiplier - 0.5)
                    elif event.key == pygame.K_d:
                        # Cycle Dispatcher
                        self.current_disp_idx = (self.current_disp_idx + 1) % len(self.dispatchers)
                        next_cls = self.dispatchers[self.current_disp_idx]
                        self.sim.dispatcher = next_cls(self.config)
                    elif event.key == pygame.K_t:
                        # Cycle Traffic Mode
                        modes = list(TrafficMode)
                        curr_i = modes.index(self.config.traffic_mode)
                        self.config.traffic_mode = modes[(curr_i + 1) % len(modes)]
                    elif event.key == pygame.K_r:
                        # Reset
                        self.sim = ElevatorSimulator(self.config, self.dispatchers[self.current_disp_idx])

            # Update Simulation Logic
            if not self.paused:
                sim_dt = dt_frame * self.speed_multiplier
                self.sim.step(sim_dt)

            # Render Frame
            self._render()
            pygame.display.flip()
            self.clock.tick(self.config.fps)

        pygame.quit()

    def _render(self):
        # Clean Background
        self.screen.fill((241, 245, 249)) # Slate 100

        # 1. Top Header Banner
        header_rect = pygame.Rect(0, 0, self.width, self.header_height)
        pygame.draw.rect(self.screen, (30, 58, 138), header_rect)

        title_surf = self.title_font.render(
            "HIERARCHICAL MULTI-AGENT AI ELEVATOR DISPATCHING SIMULATOR", True, (255, 255, 255)
        )
        self.screen.blit(title_surf, (20, 8))

        sub_text = f"CSE Capstone | Active Engine: {self.sim.dispatcher.name} | Traffic: {self.config.traffic_mode.name} | Speed: {self.speed_multiplier}x"
        sub_surf = self.small_font.render(sub_text, True, (191, 219, 254))
        self.screen.blit(sub_surf, (20, 31))

        # 2. Draw Building Structure
        self._render_building()

        # 3. Draw Elevator Cars
        self._render_elevators()

        # 4. Draw Right-Side Telemetry HUD
        self._render_hud()

    def _render_building(self):
        N = self.config.num_floors
        b_left = self.building_left
        b_right = self.building_right

        # Building background backdrop
        b_rect = pygame.Rect(b_left, self.building_top, self.building_width, self.building_bottom - self.building_top)
        pygame.draw.rect(self.screen, (255, 255, 255), b_rect)
        pygame.draw.rect(self.screen, (203, 213, 225), b_rect, 2)

        # Floor lines & Waiting queues
        for floor in range(N):
            # Floor 0 at bottom, Floor N-1 at top
            y = self.building_bottom - (floor + 1) * self.floor_height_px
            floor_line_y = y + self.floor_height_px
            pygame.draw.line(self.screen, (226, 232, 240), (b_left, floor_line_y), (b_right, floor_line_y), 1)

            # Floor Label
            lbl_text = "LOBBY" if floor == 0 else f"F{floor:02d}"
            lbl_col = (30, 58, 138) if floor == 0 else (71, 85, 105)
            lbl = self.bold_small.render(lbl_text, True, lbl_col)
            self.screen.blit(lbl, (b_left + 6, y + (self.floor_height_px / 2) - 6))

            # Passenger Waiting Badges
            queue = self.sim.floor_queues.get(floor, [])
            if queue:
                up_count = sum(1 for p in queue if p.direction == Direction.UP)
                down_count = sum(1 for p in queue if p.direction == Direction.DOWN)

                badge_x = b_left + 46
                badge_y = y + max(2, (self.floor_height_px - 14) / 2)

                if up_count > 0:
                    badge_rect = pygame.Rect(badge_x, badge_y, 24, 14)
                    pygame.draw.rect(self.screen, (219, 234, 254), badge_rect, border_radius=3)
                    pygame.draw.rect(self.screen, (37, 99, 235), badge_rect, 1, border_radius=3)
                    t = self.small_font.render(f"▲{up_count}", True, (29, 78, 216))
                    self.screen.blit(t, (badge_x + 2, badge_y + 1))
                    badge_x += 27

                if down_count > 0:
                    badge_rect = pygame.Rect(badge_x, badge_y, 24, 14)
                    pygame.draw.rect(self.screen, (254, 226, 226), badge_rect, border_radius=3)
                    pygame.draw.rect(self.screen, (220, 38, 38), badge_rect, 1, border_radius=3)
                    t = self.small_font.render(f"▼{down_count}", True, (185, 28, 28))
                    self.screen.blit(t, (badge_x + 2, badge_y + 1))

    def _render_elevators(self):
        cab_w = min(46, int(self.slot_width * 0.70))
        cab_h = max(16, int(self.floor_height_px * 0.85))

        for car in self.sim.elevators:
            # Calculate exact center of this car's shaft slot
            slot_center_x = self.shaft_area_x + (car.car_id + 0.5) * self.slot_width
            shaft_rail_x = slot_center_x
            cab_x = slot_center_x - (cab_w / 2)

            # Draw vertical guide rails
            pygame.draw.line(self.screen, (203, 213, 225), (shaft_rail_x, self.building_top), (shaft_rail_x, self.building_bottom), 2)

            # Vertical position calculation
            car_y = self.building_bottom - ((car.current_floor_pos + 1.0) * self.floor_height_px) + (self.floor_height_px - cab_h) / 2

            # Cabin Color based on capacity saturation
            ratio = car.capacity_ratio
            if ratio >= 1.0:
                cab_color = (239, 68, 68)   # Full: Red
            elif ratio > 0.65:
                cab_color = (245, 158, 11)  # Moderate: Yellow/Orange
            elif car.state == ElevatorState.IDLE:
                cab_color = (148, 163, 184) # Idle: Slate
            else:
                cab_color = (16, 185, 129)  # Active: Emerald Green

            cab_rect = pygame.Rect(cab_x, car_y, cab_w, cab_h)
            pygame.draw.rect(self.screen, cab_color, cab_rect, border_radius=4)
            pygame.draw.rect(self.screen, (15, 23, 42), cab_rect, 1, border_radius=4)

            # Passenger Count text
            p_text = f"{car.load_count}/{self.config.car_capacity}"
            p_surf = self.bold_small.render(p_text, True, (255, 255, 255))
            self.screen.blit(p_surf, (cab_x + (cab_w - p_surf.get_width()) / 2, car_y + (cab_h - p_surf.get_height()) / 2))

            # Direction indicator arrow
            if car.direction == Direction.UP:
                dir_symbol = "▲"
                dir_col = (37, 99, 235)
            elif car.direction == Direction.DOWN:
                dir_symbol = "▼"
                dir_col = (220, 38, 38)
            else:
                dir_symbol = "■"
                dir_col = (100, 116, 139)

            arrow_surf = self.bold_small.render(dir_symbol, True, dir_col)
            self.screen.blit(arrow_surf, (cab_x + cab_w + 3, car_y + max(0, (cab_h - 12) / 2)))

            # Shaft Label at top
            s_label = self.bold_small.render(f"Car {car.car_id + 1}", True, (30, 58, 138))
            self.screen.blit(s_label, (slot_center_x - (s_label.get_width() / 2), self.building_top - 16))

    def _render_hud(self):
        hud_y = self.building_top
        hud_h = self.building_bottom - self.building_top

        # HUD Panel Box (Strictly separated from building)
        panel_rect = pygame.Rect(self.hud_x, hud_y, self.hud_width, hud_h)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, border_radius=6)
        pygame.draw.rect(self.screen, (203, 213, 225), panel_rect, 2, border_radius=6)

        # Telemetry Data
        tele = self.sim.get_telemetry()

        # Section: Live KPIs
        curr_y = hud_y + 12
        h_title = self.header_font.render("LIVE TELEMETRY DASHBOARD", True, (30, 58, 138))
        self.screen.blit(h_title, (self.hud_x + 14, curr_y))
        curr_y += 24

        kpis = [
            ("Simulation Time", f"{tele['sim_time']:.1f} s"),
            ("Traffic Pattern", f"{self.config.traffic_mode.name}"),
            ("Passengers Completed", f"{tele['total_completed']} pax"),
            ("Active Waiting Queue", f"{tele['active_waiting']} pax"),
            ("Avg Waiting Time (AWT)", f"{tele['awt']:.1f} s"),
            ("Avg Journey Time (AJT)", f"{tele['ajt']:.1f} s"),
            ("Max Wait (Anti-Starve)", f"{tele['max_wait_time']:.1f} s"),
            ("Total Distance Traveled", f"{tele['total_travel_meters']:.1f} m"),
            ("Total Door Cycles", f"{tele['total_door_cycles']}"),
            ("Motor Reversals", f"{tele['total_reversals']}"),
            ("Energy & Wear Index", f"{tele['energy_index']:.1f}")
        ]

        for label, val in kpis:
            l_surf = self.font.render(label + ":", True, (71, 85, 105))
            v_surf = self.bold_small.render(val, True, (15, 23, 42))
            self.screen.blit(l_surf, (self.hud_x + 14, curr_y))
            self.screen.blit(v_surf, (self.hud_x + self.hud_width - v_surf.get_width() - 14, curr_y))
            curr_y += 18

        # Section: Interactive Controls Box
        curr_y += 10
        pygame.draw.line(self.screen, (226, 232, 240), (self.hud_x + 10, curr_y), (self.hud_x + self.hud_width - 10, curr_y), 1)
        curr_y += 10

        c_title = self.header_font.render("KEYBOARD CONTROLS", True, (30, 58, 138))
        self.screen.blit(c_title, (self.hud_x + 14, curr_y))
        curr_y += 20

        controls = [
            ("[SPACE]", "Pause / Resume"),
            ("[UP / DOWN]", "Adjust Speed (0.5x - 10x)"),
            ("[D]", "Toggle Dispatcher (H-MAS/LOOK/ETA)"),
            ("[T]", "Cycle Traffic Mode (Peak/Lobby)"),
            ("[R]", "Reset Simulation")
        ]

        for key, desc in controls:
            k_surf = self.bold_small.render(key, True, (37, 99, 235))
            d_surf = self.font.render(desc, True, (51, 65, 85))
            self.screen.blit(k_surf, (self.hud_x + 14, curr_y))
            self.screen.blit(d_surf, (self.hud_x + 105, curr_y))
            curr_y += 17
