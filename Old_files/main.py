import pygame
import math
import sys
import os
import asyncio # KRÄVS FÖR WEBBEN
import cmath
import time # By AI agent Mima 2026-02-05 17:10:10

# --- Färger ---
COLOR_BG = (15, 15, 20)
COLOR_TEXT = (220, 220, 220)
COLOR_AXIS = (120, 120, 120) 
COLOR_BTN = (60, 60, 80)
COLOR_BTN_HOVER = (80, 80, 100)

# Fasfärger
COLOR_L1 = (255, 50, 50)   # Röd
COLOR_L2 = (50, 200, 50)   # Grön
COLOR_L3 = (50, 100, 255)  # Blå
COLOR_N  = (255, 255, 255) # Vit

# By AI agent Mima 2026-02-05 17:30:00: New colors for specific labels
COLOR_P12_LABEL = (255, 255, 0) # Yellow
COLOR_P23_LABEL = (255, 0, 255) # Magenta
COLOR_P31_LABEL = (255, 165, 0) # Orange

# Fysikparametrar
VOLTAGE_RMS = 230.0
INITIAL_FREQ = 1
MAX_FREQ = 5
BASE_PIXELS_PER_AMP = 10.0 

def resource_path(relative_path):
    """Hjälpfunktion för sökvägar."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Slider:
    def __init__(self, val_range, initial_val, label, color): # Removed is_italic parameter # By AI agent Mima 2026-02-05 19:15:00
        self.min_val, self.max_val = val_range
        self.val = initial_val
        self.label = label
        self.color = color
        self.dragging = False
        self.rect = pygame.Rect(0, 0, 10, 10)

    def set_layout(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def update(self, event_list):
        mx, my = pygame.mouse.get_pos()
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(mx, my) or (abs(mx - self.rect.centerx) < self.rect.width/2 + 20 and abs(my - self.rect.centery) < 20):
                    if self.rect.x <= mx <= self.rect.right:
                        self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
        
        if self.dragging:
            mx = max(self.rect.left, min(self.rect.right, mx))
            ratio = (mx - self.rect.left) / self.rect.width
            raw_val = self.min_val + ratio * (self.max_val - self.min_val)
            self.val = round(raw_val / 10) * 10

    def draw(self, surface, font):
        pygame.draw.rect(surface, (60, 60, 60), self.rect, border_radius=5)
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.width * ratio), self.rect.height)
        pygame.draw.rect(surface, self.color, fill_rect, border_radius=5)
        
        knob_radius = int(self.rect.height)
        knob_x = self.rect.x + int(self.rect.width * ratio)
        pygame.draw.circle(surface, (200, 200, 200), (knob_x, self.rect.centery), knob_radius)
        
        # By AI agent Mima 2026-02-05 17:55:00: Custom rendering for italic 'P', subscripts, and em-dashes
        # Attempt to use a font known for good Unicode support (DejaVu Sans), or fallback to Arial.
        font_path = pygame.font.match_font('dejavusans') # By AI agent Mima 2026-02-05 17:55:00
        if font_path: # By AI agent Mima 2026-02-05 17:55:00
            display_font = pygame.font.Font(font_path, font.get_height()) # By AI agent Mima 2026-02-05 17:55:00
        else: # By AI agent Mima 2026-02-05 17:55:00
            display_font = pygame.font.SysFont("Arial", font.get_height()) # By AI agent Mima 2026-02-05 17:55:00

        parts = self.label.split(' ', 1) # Split label into 'P' and the rest
        if len(parts) > 1 and parts[0].startswith('P'):
            # Render 'P' in italic
            p_font = pygame.font.SysFont("Arial", font.get_height(), italic=True) # By AI agent Mima 2026-02-05 17:45:00
            p_surf = p_font.render(parts[0], True, self.color) # By AI agent Mima 2026-02-05 17:45:00

            # Render the rest of the label (with subscripts and em-dashes)
            rest_label = f"{parts[1]}: {int(self.val)} W" # By AI agent Mima 2026-02-05 17:45:00
            rest_surf = display_font.render(rest_label, True, self.color) # By AI agent Mima 2026-02-05 17:45:00
            
            # Combine surfaces
            total_width = p_surf.get_width() + rest_surf.get_width() # By AI agent Mima 2026-02-05 17:45:00
            total_height = max(p_surf.get_height(), rest_surf.get_height()) # By AI agent Mima 2026-02-05 17:45:00
            combined_surf = pygame.Surface((total_width, total_height), pygame.SRCALPHA) # By AI agent Mima 2026-02-05 17:45:00
            combined_surf.blit(p_surf, (0, (total_height - p_surf.get_height()) // 2)) # By AI agent Mima 2026-02-05 17:45:00
            combined_surf.blit(rest_surf, (p_surf.get_width(), (total_height - rest_surf.get_height()) // 2)) # By AI agent Mima 2026-02-05 17:45:00
            label_surf = combined_surf # By AI agent Mima 2026-02-05 17:45:00
        else:
            # Fallback for labels that don't fit the 'P' pattern
            label_surf = display_font.render(f"{self.label}: {int(self.val)} W", True, self.color) # By AI agent Mima 2026-02-05 17:45:00

        margin = max(5, int(self.rect.height * 0.5))
        surface.blit(label_surf, (self.rect.x, self.rect.y - label_surf.get_height() - margin))

class ThreePhaseSim:
    def __init__(self, width, height):
        self.time = 0.0
        self.paused = False
        self.current_freq = INITIAL_FREQ # Current simulation frequency # By AI agent Mima 2026-02-05 17:10:10
        self.max_freq = MAX_FREQ # Max simulation frequency # By AI agent Mima 2026-02-05 17:10:10
        self.last_update_time = time.time() # By AI agent Mima 2026-02-05 17:10:10

        self.base_w = 1200
        self.base_h = 800
        self.scale = 1.0
        self.pixels_per_amp = BASE_PIXELS_PER_AMP
        
        self.font_main = None
        self.font_small = None
        
        self.original_img = None
        self.scaled_img = None
        self.img_loaded = False
        
        try:
            img_path = resource_path("3fas.jpg")
            if os.path.exists(img_path):
                self.original_img = pygame.image.load(img_path)
                self.img_loaded = True
            else:
                # Försök ladda direkt om path strular på webben
                self.original_img = pygame.image.load("3fas.jpg")
                self.img_loaded = True
        except Exception as e:
            print(f"Kunde inte ladda bild: {e}")

        self.sliders_delta = [ # By AI agent Mima 2026-02-05 19:20:00
            Slider((0, 3000), 0, "P12 (L1—L2)", COLOR_P12_LABEL), # Removed is_italic=True # By AI agent Mima 2026-02-05 19:20:00
            Slider((0, 3000), 0, "P23 (L2—L3)", COLOR_P23_LABEL), # Removed is_italic=True # By AI agent Mima 2026-02-05 19:20:00
            Slider((0, 3000), 0, "P31 (L3—L1)", COLOR_P31_LABEL)  # Removed is_italic=True # By AI agent Mima 2026-02-05 19:20:00
        ]
        
        self.sliders_y = [ # By AI agent Mima 2026-02-05 19:20:00
            Slider((0, 2000), 0, "P1 (L1—N)", COLOR_L1), # Removed is_italic=True # By AI agent Mima 2026-02-05 19:20:00
            Slider((0, 2000), 0, "P2 (L2—N)", COLOR_L2), # Removed is_italic=True # By AI agent Mima 2026-02-05 19:20:00
            Slider((0, 2000), 0, "P3 (L3—N)", COLOR_L3)  # Removed is_italic=True # By AI agent Mima 2026-02-05 19:20:00
        ]
        
        self.reset_rect = pygame.Rect(0, 0, 100, 40)
        self.stop_rect = pygame.Rect(0, 0, 100, 40)
        
        self.update_layout(width, height)
        self.line_currents_data = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)] 
        self.neutral_current_data = (0.0, 0.0)

    def update_layout(self, w, h):
        self.w = w
        self.h = h
        scale_w = w / self.base_w
        scale_h = h / self.base_h
        self.scale = min(scale_w, scale_h)
        self.pixels_per_amp = BASE_PIXELS_PER_AMP * self.scale
        
        main_font_size = max(12, int(18 * self.scale))
        small_font_size = max(10, int(20 * self.scale))
        heading_font_size = max(12, int(25 * self.scale)) # New font size for headings # By AI agent Mima 2026-02-05 19:07:00

        self.font_main = pygame.font.SysFont("Arial", main_font_size)
        self.font_small = pygame.font.SysFont("Arial", small_font_size) # Removed italic, will handle for specific text # By AI agent Mima 2026-02-05 19:07:00
        self.font_heading = pygame.font.SysFont("Arial", heading_font_size, italic=True) # New font for headings, italic # By AI agent Mima 2026-02-05 19:07:00
        
        if self.img_loaded:
            target_w = w // 2 - int(50 * self.scale)
            target_h = h // 2 - int(80 * self.scale)
            img_rect = self.original_img.get_rect()
            scale_ratio = min(target_w / img_rect.width, target_h / img_rect.height)
            new_size = (int(img_rect.width * scale_ratio), int(img_rect.height * scale_ratio))
            self.scaled_img = pygame.transform.scale(self.original_img, new_size)
            
        area_start_x = w // 2 + int(20 * self.scale)
        area_width = w // 2 - int(40 * self.scale)
        col_width = (area_width - int(40 * self.scale)) // 2
        slider_h = int(10 * self.scale)
        slider_start_y = int(140 * self.scale) # Increased spacing from headings # By AI agent Mima 2026-02-05 19:10:00
        gap = int(80 * self.scale)
        
        x_col1 = area_start_x
        for i, s in enumerate(self.sliders_delta):
            s.set_layout(x_col1, slider_start_y + i * gap, col_width, slider_h)
            
        x_col2 = area_start_x + col_width + int(40 * self.scale)
        for i, s in enumerate(self.sliders_y):
            s.set_layout(x_col2, slider_start_y + i * gap, col_width, slider_h)
            
        btn_w = int(120 * self.scale)
        btn_h = int(40 * self.scale)
        self.reset_rect = pygame.Rect(x_col2, slider_start_y + 3 * gap, btn_w, btn_h)
        self.stop_rect = pygame.Rect(w // 2 - btn_w - int(20 * self.scale), h - int(60 * self.scale), btn_w, btn_h) # Moved left # By AI agent Mima 2026-02-05 19:25:00

    def update(self, events):
        current_time = time.time() # By AI agent Mima 2026-02-05 17:10:10
        dt = current_time - self.last_update_time # By AI agent Mima 2026-02-05 17:10:10
        self.last_update_time = current_time # By AI agent Mima 2026-02-05 17:10:10

        if not self.paused:
            # Update simulation speed using delta time # By AI agent Mima 2026-02-05 17:10:10
            self.time += self.current_freq * dt # By AI agent Mima 2026-02-05 17:10:10
            self.current_freq = min(self.current_freq, self.max_freq) # By AI agent Mima 2026-02-05 17:10:10
            
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.reset_rect.collidepoint(mx, my):
                    for s in self.sliders_y: s.val = 0.0
                    for s in self.sliders_delta: s.val = 0.0
                if self.stop_rect.collidepoint(mx, my):
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                        self.time = 0.0
            if event.type == pygame.VIDEORESIZE:
                self.update_layout(event.w, event.h)
                
        for s in self.sliders_y: s.update(events)
        for s in self.sliders_delta: s.update(events)
        self.calculate_currents()

    def calculate_currents(self):
        u_phase = [cmath.rect(1, 0), cmath.rect(1, -2 * math.pi / 3), cmath.rect(1, -4 * math.pi / 3)]
        u_line = [cmath.rect(1, math.pi / 6), cmath.rect(1, -math.pi / 2), cmath.rect(1, -7 * math.pi / 6)]
        
        i_y = []
        for i in range(3):
            p = self.sliders_y[i].val
            mag = p / VOLTAGE_RMS
            i_y.append(mag * u_phase[i])
            
        u_line_rms = VOLTAGE_RMS * math.sqrt(3)
        i_d = []
        for i in range(3):
            p = self.sliders_delta[i].val
            mag = p / u_line_rms
            i_d.append(mag * u_line[i])
        
        i_total = [
            i_y[0] + i_d[0] - i_d[2],
            i_y[1] + i_d[1] - i_d[0],
            i_y[2] + i_d[2] - i_d[1]
        ]
        
        self.line_currents_data = []
        for i_ph in i_total:
            mag = abs(i_ph)
            angle = cmath.phase(i_ph)
            self.line_currents_data.append((mag * self.pixels_per_amp, angle))
            
        i_n_vec = (i_total[0] + i_total[1] + i_total[2])
        self.neutral_current_data = (abs(i_n_vec) * self.pixels_per_amp, cmath.phase(i_n_vec))

    def draw_button(self, surface, rect, text):
        mx, my = pygame.mouse.get_pos()
        col = COLOR_BTN_HOVER if rect.collidepoint(mx, my) else COLOR_BTN
        border_radius = int(5 * self.scale)
        pygame.draw.rect(surface, col, rect, border_radius=border_radius)
        pygame.draw.rect(surface, (150, 150, 150), rect, max(1, int(2 * self.scale)), border_radius=border_radius)
        txt = self.font_main.render(text, True, COLOR_TEXT)
        surface.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def draw_circuit_section(self, surface):
        title = self.font_main.render(f"Kopplingsschema (Ueff = {int(VOLTAGE_RMS)} V)", True, (150, 150, 150))
        surface.blit(title, (int(20 * self.scale), int(20 * self.scale)))
        if self.img_loaded and self.scaled_img:
            area_w = self.w // 2
            area_h = self.h // 2
            img_x = (area_w - self.scaled_img.get_width()) // 2
            img_y = (area_h - self.scaled_img.get_height()) // 2 + int(20 * self.scale)
            surface.blit(self.scaled_img, (img_x, img_y))
        else:
            msg = self.font_main.render("Bild saknas", True, (255, 100, 100))
            surface.blit(msg, (int(100 * self.scale), int(100 * self.scale)))

    def draw_controls_section(self, surface):
        title = self.font_main.render("Justera belastning", True, (150, 150, 150))
        surface.blit(title, (self.w // 2 + int(20 * self.scale), int(20 * self.scale)))
        col1_x = self.sliders_delta[0].rect.x
        col2_x = self.sliders_y[0].rect.x
        DELTA = "\u0394"
        head1 = self.font_heading.render(f"Huvudspänning ({DELTA})", True, (180, 180, 180)) # Use new heading font # By AI agent Mima 2026-02-05 19:10:00
        head2 = self.font_heading.render("Fasspänning (Y)", True, (180, 180, 180)) # Use new heading font # By AI agent Mima 2026-02-05 19:10:00
        surface.blit(head1, (col1_x, int(60 * self.scale)))
        surface.blit(head2, (col2_x, int(60 * self.scale)))
        for s in self.sliders_delta: s.draw(surface, self.font_main)
        for s in self.sliders_y: s.draw(surface, self.font_main)
        self.draw_button(surface, self.reset_rect, "Reset (0 W)")

    def draw_arrow(self, surface, color, start, end, width=3, head_size=15):
        scaled_width = max(1, int(width * self.scale))
        scaled_head = int(head_size * self.scale)
        pygame.draw.line(surface, color, start, end, scaled_width)
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if math.hypot(dx, dy) < 5 * self.scale: return
        angle = math.atan2(dy, dx)
        arrow_angle = math.pi / 6
        p1 = end
        p2 = (end[0] - scaled_head * math.cos(angle - arrow_angle), end[1] - scaled_head * math.sin(angle - arrow_angle))
        p3 = (end[0] - scaled_head * math.cos(angle + arrow_angle), end[1] - scaled_head * math.sin(angle + arrow_angle))
        pygame.draw.polygon(surface, color, [p1, p2, p3])

    def draw_dashed_line(self, surface, color, start, end, width=1):
        scaled_width = max(1, int(width * self.scale))
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        dash_len = int(5 * self.scale)
        gap_len = int(5 * self.scale)
        curr_dist = 0
        while curr_dist < dist:
            p_start = (start[0] + math.cos(angle) * curr_dist, start[1] + math.sin(angle) * curr_dist)
            p_end = (start[0] + math.cos(angle) * min(curr_dist + dash_len, dist), 
                     start[1] + math.sin(angle) * min(curr_dist + dash_len, dist))
            pygame.draw.line(surface, color, p_start, p_end, scaled_width)
            curr_dist += dash_len + gap_len

    def draw_horizontal_dashed_line(self, surface, color, start_x, end_x, y, width=1):
        if end_x < start_x: start_x, end_x = end_x, start_x
        dash_len = int(4 * self.scale)
        gap_len = int(4 * self.scale)
        scaled_width = max(1, int(width * self.scale))
        curr_x = start_x
        while curr_x < end_x:
            next_x = min(curr_x + dash_len, end_x)
            pygame.draw.line(surface, color, (curr_x, y), (next_x, y), scaled_width)
            curr_x += dash_len + gap_len

    def draw_phasor_diagram(self, surface):
        cx = self.w // 4
        cy = int(self.h * 0.75)
        sine_axis_x = self.w // 2 + int(80 * self.scale)
        title = self.font_main.render("Visardiagram", True, (150, 150, 150))
        surface.blit(title, (int(20 * self.scale), self.h // 2 + int(20 * self.scale)))
        axis_len = int(100 * self.scale)
        pygame.draw.line(surface, COLOR_AXIS, (cx - axis_len, cy), (cx + axis_len, cy), 1)
        pygame.draw.line(surface, COLOR_AXIS, (cx, cy - axis_len), (cx, cy + axis_len), 1)
        phase_offsets = [0, math.radians(120), math.radians(240)] 
        colors = [COLOR_L1, COLOR_L2, COLOR_L3]
        e_labels = ["e1", "e2", "e3"]
        
        for i in range(3):
            theta_e = self.time - phase_offsets[i]
            vx_e = axis_len * math.cos(theta_e)
            vy_e = -axis_len * math.sin(theta_e)
            end_x_e = cx + vx_e
            end_y_e = cy + vy_e
            self.draw_dashed_line(surface, COLOR_N, (cx, cy), (end_x_e, end_y_e), width=1)
            lbl_x = end_x_e + (20 * self.scale) * math.cos(theta_e)
            lbl_y = end_y_e - (20 * self.scale) * math.sin(theta_e)
            lbl = self.font_small.render(e_labels[i], True, COLOR_N)
            surface.blit(lbl, (lbl_x - lbl.get_width()//2, lbl_y - lbl.get_height()//2))

        sum_mag = 0
        vectors = []
        for i in range(3):
            mag_px, angle_rad = self.line_currents_data[i]
            theta = self.time + angle_rad
            vx = mag_px * math.cos(theta)
            vy = -mag_px * math.sin(theta)
            vectors.append((vx, vy))
            sum_mag += mag_px
            
        n_mag, n_angle = self.neutral_current_data
        if n_mag > 2 * self.scale:
            theta_n = self.time + n_angle
            vx_n = n_mag * math.cos(theta_n)
            vy_n = -n_mag * math.sin(theta_n)
            self.draw_arrow(surface, COLOR_N, (cx, cy), (cx + vx_n, cy + vy_n), width=4)
            in_amp = n_mag / self.pixels_per_amp 
            label_n = self.font_main.render(f"iN: {in_amp:.1f} A", True, COLOR_N)
            surface.blit(label_n, (cx + vx_n + 10, cy + vy_n))

        for i in range(3):
            vx, vy = vectors[i]
            end_x = cx + vx
            end_y = cy + vy
            self.draw_horizontal_dashed_line(surface, colors[i], end_x, sine_axis_x, end_y, width=1)
            self.draw_arrow(surface, colors[i], (cx, cy), (end_x, end_y), width=3)
            
        btn_text = "Start" if self.paused else "Stopp (t=0)"
        self.draw_button(surface, self.stop_rect, btn_text)

    def draw_sine_waves(self, surface):
        offset_x = self.w // 2 + int(80 * self.scale)
        offset_y = int(self.h * 0.75)
        width = self.w // 2 - int(120 * self.scale)
        height_scale = int(150 * self.scale)
        title = self.font_main.render("Momentanvärden", True, (150, 150, 150))
        surface.blit(title, (offset_x, self.h // 2 + int(20 * self.scale)))
        pygame.draw.line(surface, COLOR_AXIS, (offset_x, offset_y), (offset_x + width, offset_y), 1)
        pygame.draw.line(surface, COLOR_AXIS, (offset_x, offset_y - height_scale), (offset_x, offset_y + height_scale), 1)
        
        ticks = [-15, -10, -5, 0, 5, 10, 15] 
        for amp in ticks:
            px_val = amp * self.pixels_per_amp
            y_pos = offset_y - px_val
            if offset_y - height_scale <= y_pos <= offset_y + height_scale:
                pygame.draw.line(surface, (80, 80, 80), (offset_x, y_pos), (offset_x + width, y_pos), 1)
                txt_x = offset_x + int(5 * self.scale) # Moved closer to y-axis and right-aligned # By AI agent Mima 2026-02-05 19:28:00
                lbl = self.font_small.render(f"{amp} A", True, (255, 255, 255)) # Right-adjusted with space before A # By AI agent Mima 2026-02-05 19:10:00
                surface.blit(lbl, (txt_x, y_pos - int(8 * self.scale))) # By AI agent Mima 2026-02-05 19:10:00

        colors = [COLOR_L1, COLOR_L2, COLOR_L3]
        points_lists = [[], [], [], []] 
        step = max(2, int(2 * self.scale))
        
        for x in range(0, width, step):
            t_offset = x * 0.05
            sum_y_val = 0
            for i in range(3):
                mag_px, angle_rad = self.line_currents_data[i]
                theta = self.time + t_offset + angle_rad
                y_val = mag_px * math.sin(theta)
                points_lists[i].append((offset_x + x, offset_y - y_val))
            n_mag, n_angle = self.neutral_current_data
            theta_n = self.time + t_offset + n_angle
            y_val_n = n_mag * math.sin(theta_n)
            points_lists[3].append((offset_x + x, offset_y - y_val_n))

        scaled_line_width = max(2, int(2 * self.scale))
        neutral_width = max(3, int(3 * self.scale))
        if len(points_lists[3]) > 1:
            pygame.draw.lines(surface, COLOR_N, False, points_lists[3], neutral_width)
        for i in range(3):
            if len(points_lists[i]) > 1:
                pygame.draw.lines(surface, colors[i], False, points_lists[i], scaled_line_width)

async def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Trefas-simulator: Y-koppling")
    clock = pygame.time.Clock()
    
    sim = ThreePhaseSim(1200, 800)
    
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        sim.update(events)
        
        screen.fill(COLOR_BG)
        
        w, h = screen.get_size()
        pygame.draw.line(screen, (40, 40, 50), (w//2, 0), (w//2, h), 2)
        pygame.draw.line(screen, (40, 40, 50), (0, h//2), (w, h//2), 2)
        
        sim.draw_circuit_section(screen)
        sim.draw_controls_section(screen)
        sim.draw_phasor_diagram(screen)
        sim.draw_sine_waves(screen)

        pygame.display.flip()
        
        # VIKTIGT FÖR WEBBEN: yield control to browser
        await asyncio.sleep(0)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())