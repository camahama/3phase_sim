import pygame
import math
import sys
import os

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

# Fysikparametrar
VOLTAGE_RMS = 230.0
FREQ = 0.02
BASE_PIXELS_PER_AMP = 10.0 

def resource_path(relative_path):
    """Hjälpfunktion för sökvägar (PyInstaller)."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Slider:
    def __init__(self, val_range, initial_val, label, color):
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
            self.val = self.min_val + ratio * (self.max_val - self.min_val)

    def draw(self, surface, font):
        pygame.draw.rect(surface, (60, 60, 60), self.rect, border_radius=5)
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.width * ratio), self.rect.height)
        pygame.draw.rect(surface, self.color, fill_rect, border_radius=5)
        
        # Knoppen skalar med höjden på slidern
        knob_radius = int(self.rect.height)
        knob_x = self.rect.x + int(self.rect.width * ratio)
        pygame.draw.circle(surface, (200, 200, 200), (knob_x, self.rect.centery), knob_radius)
        
        label_surf = font.render(f"{self.label}: {int(self.val)} W", True, self.color)
        # Placera texten strax ovanför, med lite marginal som också kan skalas
        margin = max(5, int(self.rect.height * 0.5))
        surface.blit(label_surf, (self.rect.x, self.rect.y - label_surf.get_height() - margin))

class ThreePhaseSim:
    def __init__(self, width, height):
        self.time = 0.0
        
        # Basstorlek för att beräkna skalning
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
            self.original_img = pygame.image.load(img_path)
            self.img_loaded = True
        except FileNotFoundError:
            print("Kunde inte hitta '3fas.jpg'.")

        # Initiera med 0 W
        self.sliders = [
            Slider((0, 2000), 0, "P1 (Effekt L1)", COLOR_L1),
            Slider((0, 2000), 0, "P2 (Effekt L2)", COLOR_L2),
            Slider((0, 2000), 0, "P3 (Effekt L3)", COLOR_L3)
        ]
        
        self.reset_rect = pygame.Rect(0, 0, 100, 40)
        self.update_layout(width, height)
        self.amps_px = [0.0, 0.0, 0.0]
        self.amps_phys = [0.0, 0.0, 0.0]

    def update_layout(self, w, h):
        self.w = w
        self.h = h
        
        # Beräkna global skalfaktor (minsta av bredd/höjd-förhållandet)
        scale_w = w / self.base_w
        scale_h = h / self.base_h
        self.scale = min(scale_w, scale_h)
        
        # Uppdatera konstanter baserat på skala
        self.pixels_per_amp = BASE_PIXELS_PER_AMP * self.scale
        
        # Skapa skalade fonter
        # Vi tvingar en minimistorlek så det förblir läsbart
        main_font_size = max(12, int(18 * self.scale))
        small_font_size = max(10, int(20 * self.scale))
        self.font_main = pygame.font.SysFont("Arial", main_font_size)
        self.font_small = pygame.font.Font(None, small_font_size)
        
        # 1. Skala bild
        if self.img_loaded:
            target_w = w // 2 - int(50 * self.scale)
            target_h = h // 2 - int(80 * self.scale)
            img_rect = self.original_img.get_rect()
            scale_ratio = min(target_w / img_rect.width, target_h / img_rect.height)
            new_size = (int(img_rect.width * scale_ratio), int(img_rect.height * scale_ratio))
            self.scaled_img = pygame.transform.scale(self.original_img, new_size)
            
        # 2. Sliders
        slider_x = w // 2 + int(50 * self.scale)
        slider_w = w // 2 - int(100 * self.scale)
        slider_h = int(10 * self.scale)
        slider_start_y = int(100 * self.scale)
        gap = int(80 * self.scale)
        
        for i, s in enumerate(self.sliders):
            s.set_layout(slider_x, slider_start_y + i * gap, slider_w, slider_h)
            
        # Reset knapp
        btn_w = int(120 * self.scale)
        btn_h = int(40 * self.scale)
        self.reset_rect = pygame.Rect(slider_x, slider_start_y + 3 * gap, btn_w, btn_h)

    def update(self, events):
        self.time += FREQ
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.reset_rect.collidepoint(mx, my):
                    for s in self.sliders:
                        s.val = 1000.0 # Reset till 1 kW
            if event.type == pygame.VIDEORESIZE:
                self.update_layout(event.w, event.h)
                
        for slider in self.sliders:
            slider.update(events)
            
        for i in range(3):
            power_watts = self.sliders[i].val
            i_rms = power_watts / VOLTAGE_RMS
            i_peak = i_rms * math.sqrt(2)
            self.amps_phys[i] = i_peak
            self.amps_px[i] = i_peak * self.pixels_per_amp

    def draw_reset_button(self, surface):
        mx, my = pygame.mouse.get_pos()
        col = COLOR_BTN_HOVER if self.reset_rect.collidepoint(mx, my) else COLOR_BTN
        border_radius = int(5 * self.scale)
        pygame.draw.rect(surface, col, self.reset_rect, border_radius=border_radius)
        pygame.draw.rect(surface, (150, 150, 150), self.reset_rect, max(1, int(2 * self.scale)), border_radius=border_radius)
        
        txt = self.font_main.render("Reset (1kW)", True, COLOR_TEXT)
        surface.blit(txt, (self.reset_rect.centerx - txt.get_width()//2, self.reset_rect.centery - txt.get_height()//2))

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
        title = self.font_main.render("Justera Belastning (Effekt)", True, (150, 150, 150))
        surface.blit(title, (self.w // 2 + int(20 * self.scale), int(20 * self.scale)))
        
        for slider in self.sliders:
            slider.draw(surface, self.font_main)
        self.draw_reset_button(surface)

    def draw_arrow(self, surface, color, start, end, width=3, head_size=15):
        # Skala pilens storlek
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
        vectors = []
        sum_x, sum_y = 0, 0
        
        for i in range(3):
            theta = self.time - phase_offsets[i]
            mag = self.amps_px[i]
            vx = mag * math.cos(theta)
            vy = -mag * math.sin(theta)
            vectors.append((vx, vy))
            sum_x += vx
            sum_y += vy
            
        if math.hypot(sum_x, sum_y) > 2 * self.scale: 
            end_nx = cx + sum_x
            end_ny = cy + sum_y
            self.draw_arrow(surface, COLOR_N, (cx, cy), (end_nx, end_ny), width=4)
            in_amp = math.hypot(sum_x, sum_y) / self.pixels_per_amp / math.sqrt(2)
            label_n = self.font_main.render(f"iN: {in_amp:.1f} A", True, COLOR_N)
            surface.blit(label_n, (end_nx + 10, end_ny))
            
        for i in range(3):
            vx, vy = vectors[i]
            end_x = cx + vx
            end_y = cy + vy
            self.draw_horizontal_dashed_line(surface, colors[i], end_x, sine_axis_x, end_y, width=1)
            self.draw_arrow(surface, colors[i], (cx, cy), (end_x, end_y), width=3)

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
            pygame.draw.line(surface, (80, 80, 80), (offset_x, y_pos), (offset_x + width, y_pos), 1)
            txt_x = max(10, offset_x - int(45 * self.scale))
            lbl = self.font_small.render(f"{amp}A", True, (255, 255, 255))
            surface.blit(lbl, (txt_x, y_pos - int(8 * self.scale)))

        colors = [COLOR_L1, COLOR_L2, COLOR_L3]
        phases = [0, math.radians(120), math.radians(240)]
        points_lists = [[], [], [], []] 
        
        # Sampla färre punkter om bredden är liten för prestanda
        step = max(2, int(2 * self.scale))
        
        for x in range(0, width, step):
            t_offset = x * 0.05
            sum_y_val = 0
            for i in range(3):
                theta = (self.time + t_offset) - phases[i]
                y_val = self.amps_px[i] * math.sin(theta)
                sum_y_val += y_val
                points_lists[i].append((offset_x + x, offset_y - y_val))
            points_lists[3].append((offset_x + x, offset_y - sum_y_val))

        scaled_line_width = max(2, int(2 * self.scale))
        neutral_width = max(3, int(3 * self.scale))

        if len(points_lists[3]) > 1:
            pygame.draw.lines(surface, COLOR_N, False, points_lists[3], neutral_width)
        for i in range(3):
            if len(points_lists[i]) > 1:
                pygame.draw.lines(surface, colors[i], False, points_lists[i], scaled_line_width)

def main():
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
            # VIDEORESIZE hanteras inuti sim.update()
        
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
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()