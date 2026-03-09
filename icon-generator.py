import pygame
import math

# Konfigurera ikonstorlek (macOS gillar stora ikoner, 1024x1024)
SIZE = 1024
CENTER = SIZE // 2
RADIUS = 350
BG_COLOR = (25, 25, 30) # Samma mörka färg som appen
L1_COLOR = (255, 50, 50)
L2_COLOR = (50, 200, 50)
L3_COLOR = (50, 100, 255)

pygame.init()
surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

# 1. Rita bakgrund (Rundad fyrkant - "Squircle")
# På Mac sköter OSen maskningen, men vi ritar en fylld bakgrund
pygame.draw.rect(surf, BG_COLOR, (0, 0, SIZE, SIZE), border_radius=200)

# 2. Rita en stiliserad Y-koppling
width = 80
center_pt = (CENTER, CENTER)

# Vinklar för faserna
angles = [90, 330, 210] # Justerade för att se snygga ut på en ikon (L1 uppåt)
colors = [L1_COLOR, L2_COLOR, L3_COLOR]

# Rita linjerna
for i in range(3):
    rad = math.radians(angles[i])
    end_x = CENTER + RADIUS * math.cos(rad)
    end_y = CENTER - RADIUS * math.sin(rad) # Minus för att y går neråt
    
    pygame.draw.line(surf, colors[i], center_pt, (end_x, end_y), width)
    
    # Rita en cirkel i änden för "mjukare" känsla
    pygame.draw.circle(surf, colors[i], (end_x, end_y), width // 2)

# Rita mitten-cirkel (Neutral)
pygame.draw.circle(surf, (220, 220, 220), center_pt, width // 2 + 10)

# Spara bilden
pygame.image.save(surf, "app_icon.png")
print("Ikon sparad som 'app_icon.png'")
pygame.quit()