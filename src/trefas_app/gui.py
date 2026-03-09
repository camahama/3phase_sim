import math

import pygame

from .physics import BASE_PIXELS_PER_AMP, VOLTAGE_RMS

# UI colors
COLOR_BG = (15, 15, 20)
COLOR_TEXT = (220, 220, 220)
COLOR_AXIS = (120, 120, 120)
COLOR_BTN = (60, 60, 80)
COLOR_BTN_HOVER = (80, 80, 100)

COLOR_L1 = (255, 50, 50)
COLOR_L2 = (50, 200, 50)
COLOR_L3 = (50, 100, 255)
COLOR_N = (255, 255, 255)

COLOR_P12_LABEL = (255, 255, 0)
COLOR_P23_LABEL = (255, 0, 255)
COLOR_P31_LABEL = (255, 165, 0)


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
                near_knob = (
                    abs(mx - self.rect.centerx) < self.rect.width / 2 + 20
                    and abs(my - self.rect.centery) < 20
                )
                if (self.rect.collidepoint(mx, my) or near_knob) and self.rect.x <= mx <= self.rect.right:
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

        label_surf = font.render(f"{self.label}: {int(self.val)} W", True, self.color)
        margin = max(5, int(self.rect.height * 0.5))
        surface.blit(label_surf, (self.rect.x, self.rect.y - label_surf.get_height() - margin))


class ThreePhaseGUI:
    """Handles all input widgets and rendering. Uses model for simulation data."""

    def __init__(self, width, height, model, image_loader):
        self.model = model
        self.image_loader = image_loader

        self.base_w = 1200
        self.base_h = 800
        self.scale = 1.0
        self.pixels_per_amp = BASE_PIXELS_PER_AMP

        self.font_main = None
        self.font_small = None
        self.font_heading = None

        self.original_img = None
        self.scaled_img = None
        self.img_loaded = False

        self._load_image()

        self.sliders_delta = [
            Slider((0, 3000), 0, "P12 (L1-L2)", COLOR_P12_LABEL),
            Slider((0, 3000), 0, "P23 (L2-L3)", COLOR_P23_LABEL),
            Slider((0, 3000), 0, "P31 (L3-L1)", COLOR_P31_LABEL),
        ]

        self.sliders_y = [
            Slider((0, 2000), 0, "P1 (L1-N)", COLOR_L1),
            Slider((0, 2000), 0, "P2 (L2-N)", COLOR_L2),
            Slider((0, 2000), 0, "P3 (L3-N)", COLOR_L3),
        ]

        self.reset_rect = pygame.Rect(0, 0, 100, 40)
        self.stop_rect = pygame.Rect(0, 0, 100, 40)

        self.update_layout(width, height)
        self._sync_model_from_sliders()

    def _load_image(self):
        try:
            img_path = self.image_loader("3fas.jpg")
            self.original_img = pygame.image.load(img_path)
            self.img_loaded = True
        except Exception as exc:
            print(f"Kunde inte ladda bild: {exc}")

    def _sync_model_from_sliders(self):
        self.model.sliders_y = [s.val for s in self.sliders_y]
        self.model.sliders_delta = [s.val for s in self.sliders_delta]
        self.model.calculate_currents(self.pixels_per_amp)

    def update_layout(self, w, h):
        self.w = w
        self.h = h
        scale_w = w / self.base_w
        scale_h = h / self.base_h
        self.scale = min(scale_w, scale_h)
        self.pixels_per_amp = BASE_PIXELS_PER_AMP * self.scale

        main_font_size = max(12, int(18 * self.scale))
        small_font_size = max(10, int(20 * self.scale))
        heading_font_size = max(12, int(25 * self.scale))

        self.font_main = pygame.font.SysFont("Arial", main_font_size)
        self.font_small = pygame.font.SysFont("Arial", small_font_size)
        self.font_heading = pygame.font.SysFont("Arial", heading_font_size, italic=True)

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
        slider_start_y = int(140 * self.scale)
        gap = int(80 * self.scale)

        x_col1 = area_start_x
        for i, slider in enumerate(self.sliders_delta):
            slider.set_layout(x_col1, slider_start_y + i * gap, col_width, slider_h)

        x_col2 = area_start_x + col_width + int(40 * self.scale)
        for i, slider in enumerate(self.sliders_y):
            slider.set_layout(x_col2, slider_start_y + i * gap, col_width, slider_h)

        btn_w = int(120 * self.scale)
        btn_h = int(40 * self.scale)
        self.reset_rect = pygame.Rect(x_col2, slider_start_y + 3 * gap, btn_w, btn_h)
        self.stop_rect = pygame.Rect(
            w // 2 - btn_w - int(20 * self.scale),
            h - int(60 * self.scale),
            btn_w,
            btn_h,
        )

    def update(self, events, dt):
        self.model.update_time(dt)

        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.reset_rect.collidepoint(mx, my):
                    for slider in self.sliders_y:
                        slider.val = 0.0
                    for slider in self.sliders_delta:
                        slider.val = 0.0
                    self.model.reset_loads()
                if self.stop_rect.collidepoint(mx, my):
                    self.model.toggle_pause()
            if event.type == pygame.VIDEORESIZE:
                self.update_layout(event.w, event.h)

        for slider in self.sliders_y:
            slider.update(events)
        for slider in self.sliders_delta:
            slider.update(events)

        self._sync_model_from_sliders()

    def draw_button(self, surface, rect, text):
        mx, my = pygame.mouse.get_pos()
        color = COLOR_BTN_HOVER if rect.collidepoint(mx, my) else COLOR_BTN
        border_radius = int(5 * self.scale)
        pygame.draw.rect(surface, color, rect, border_radius=border_radius)
        pygame.draw.rect(surface, (150, 150, 150), rect, max(1, int(2 * self.scale)), border_radius=border_radius)
        txt = self.font_main.render(text, True, COLOR_TEXT)
        surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

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
        head1 = self.font_heading.render("Huvudspanning (Delta)", True, (180, 180, 180))
        head2 = self.font_heading.render("Fasspanning (Y)", True, (180, 180, 180))
        surface.blit(head1, (col1_x, int(60 * self.scale)))
        surface.blit(head2, (col2_x, int(60 * self.scale)))

        for slider in self.sliders_delta:
            slider.draw(surface, self.font_main)
        for slider in self.sliders_y:
            slider.draw(surface, self.font_main)

        self.draw_button(surface, self.reset_rect, "Reset (0 W)")

    def draw_arrow(self, surface, color, start, end, width=3, head_size=15):
        scaled_width = max(1, int(width * self.scale))
        scaled_head = int(head_size * self.scale)
        pygame.draw.line(surface, color, start, end, scaled_width)
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if math.hypot(dx, dy) < 5 * self.scale:
            return

        angle = math.atan2(dy, dx)
        arrow_angle = math.pi / 6
        p1 = end
        p2 = (
            end[0] - scaled_head * math.cos(angle - arrow_angle),
            end[1] - scaled_head * math.sin(angle - arrow_angle),
        )
        p3 = (
            end[0] - scaled_head * math.cos(angle + arrow_angle),
            end[1] - scaled_head * math.sin(angle + arrow_angle),
        )
        pygame.draw.polygon(surface, color, [p1, p2, p3])

    def draw_dashed_line(self, surface, color, start, end, width=1):
        scaled_width = max(1, int(width * self.scale))
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        dash_len = int(5 * self.scale)
        gap_len = int(5 * self.scale)

        curr_dist = 0
        while curr_dist < distance:
            p_start = (start[0] + math.cos(angle) * curr_dist, start[1] + math.sin(angle) * curr_dist)
            p_end = (
                start[0] + math.cos(angle) * min(curr_dist + dash_len, distance),
                start[1] + math.sin(angle) * min(curr_dist + dash_len, distance),
            )
            pygame.draw.line(surface, color, p_start, p_end, scaled_width)
            curr_dist += dash_len + gap_len

    def draw_horizontal_dashed_line(self, surface, color, start_x, end_x, y, width=1):
        if end_x < start_x:
            start_x, end_x = end_x, start_x
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
            theta_e = self.model.time - phase_offsets[i]
            vx_e = axis_len * math.cos(theta_e)
            vy_e = -axis_len * math.sin(theta_e)
            end_x_e = cx + vx_e
            end_y_e = cy + vy_e
            self.draw_dashed_line(surface, COLOR_N, (cx, cy), (end_x_e, end_y_e), width=1)
            lbl_x = end_x_e + (20 * self.scale) * math.cos(theta_e)
            lbl_y = end_y_e - (20 * self.scale) * math.sin(theta_e)
            lbl = self.font_small.render(e_labels[i], True, COLOR_N)
            surface.blit(lbl, (lbl_x - lbl.get_width() // 2, lbl_y - lbl.get_height() // 2))

        vectors = []
        for i in range(3):
            mag_px, angle_rad = self.model.line_currents_data[i]
            theta = self.model.time + angle_rad
            vx = mag_px * math.cos(theta)
            vy = -mag_px * math.sin(theta)
            vectors.append((vx, vy))

        n_mag, n_angle = self.model.neutral_current_data
        if n_mag > 2 * self.scale:
            theta_n = self.model.time + n_angle
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

        btn_text = "Start" if self.model.paused else "Stopp (t=0)"
        self.draw_button(surface, self.stop_rect, btn_text)

    def draw_sine_waves(self, surface):
        offset_x = self.w // 2 + int(80 * self.scale)
        offset_y = int(self.h * 0.75)
        width = self.w // 2 - int(120 * self.scale)
        height_scale = int(150 * self.scale)

        title = self.font_main.render("Momentanvarden", True, (150, 150, 150))
        surface.blit(title, (offset_x, self.h // 2 + int(20 * self.scale)))
        pygame.draw.line(surface, COLOR_AXIS, (offset_x, offset_y), (offset_x + width, offset_y), 1)
        pygame.draw.line(surface, COLOR_AXIS, (offset_x, offset_y - height_scale), (offset_x, offset_y + height_scale), 1)

        ticks = [-15, -10, -5, 0, 5, 10, 15]
        for amp in ticks:
            px_val = amp * self.pixels_per_amp
            y_pos = offset_y - px_val
            if offset_y - height_scale <= y_pos <= offset_y + height_scale:
                pygame.draw.line(surface, (80, 80, 80), (offset_x, y_pos), (offset_x + width, y_pos), 1)
                txt_x = offset_x + int(5 * self.scale)
                lbl = self.font_small.render(f"{amp} A", True, (255, 255, 255))
                surface.blit(lbl, (txt_x, y_pos - int(8 * self.scale)))

        colors = [COLOR_L1, COLOR_L2, COLOR_L3]
        points_lists = [[], [], [], []]
        step = max(2, int(2 * self.scale))

        for x in range(0, width, step):
            t_offset = x * 0.05
            for i in range(3):
                mag_px, angle_rad = self.model.line_currents_data[i]
                theta = self.model.time + t_offset + angle_rad
                y_val = mag_px * math.sin(theta)
                points_lists[i].append((offset_x + x, offset_y - y_val))

            n_mag, n_angle = self.model.neutral_current_data
            theta_n = self.model.time + t_offset + n_angle
            y_val_n = n_mag * math.sin(theta_n)
            points_lists[3].append((offset_x + x, offset_y - y_val_n))

        scaled_line_width = max(2, int(2 * self.scale))
        neutral_width = max(3, int(3 * self.scale))
        if len(points_lists[3]) > 1:
            pygame.draw.lines(surface, COLOR_N, False, points_lists[3], neutral_width)
        for i in range(3):
            if len(points_lists[i]) > 1:
                pygame.draw.lines(surface, colors[i], False, points_lists[i], scaled_line_width)

    def draw(self, screen):
        screen.fill(COLOR_BG)
        pygame.draw.line(screen, (40, 40, 50), (self.w // 2, 0), (self.w // 2, self.h), 2)
        pygame.draw.line(screen, (40, 40, 50), (0, self.h // 2), (self.w, self.h // 2), 2)

        self.draw_circuit_section(screen)
        self.draw_controls_section(screen)
        self.draw_phasor_diagram(screen)
        self.draw_sine_waves(screen)
