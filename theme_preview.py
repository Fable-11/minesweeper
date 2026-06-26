import ctypes
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

import pygame
import sys

pygame.init()

THEMES = {
    "1: CLASSIC": {
        "bg":         (0x6B, 0x3A, 0x2A),
        "unrevealed": (0xD4, 0xA5, 0x74),
        "revealed":   (0xF0, 0xD5, 0xB0),
        "bar":        (0x8B, 0x5E, 0x3C),
        "grid":       (0x8B, 0x5E, 0x3C),
        "hover":      (0xDE, 0xB3, 0x84),
        "border_l":   (0xE8, 0xC9, 0xA0),
        "border_d":   (0xA0, 0x78, 0x50),
        "num1":       (0x00, 0x00, 0xFF),
        "num2":       (0x00, 0x80, 0x00),
        "num3":       (0xFF, 0x00, 0x00),
        "num4":       (0x00, 0x00, 0x80),
        "exploded":   (0xE0, 0x40, 0x40),
        "win":        (0x80, 0xE0, 0x80),
    },
    "2: SUNSET GLOW": {
        "bg":         (0x2D, 0x1B, 0x3D),
        "unrevealed": (0xE8, 0x8D, 0x56),
        "revealed":   (0xFD, 0xE8, 0xCD),
        "bar":        (0x8B, 0x3A, 0x62),
        "grid":       (0x8B, 0x3A, 0x62),
        "hover":      (0xF2, 0xA8, 0x6B),
        "border_l":   (0xF5, 0xC0, 0x80),
        "border_d":   (0xB8, 0x68, 0x40),
        "num1":       (0xFF, 0x66, 0x99),
        "num2":       (0xFF, 0xCC, 0x33),
        "num3":       (0xFF, 0x44, 0x44),
        "num4":       (0x88, 0x44, 0xCC),
        "exploded":   (0xFF, 0x33, 0x33),
        "win":        (0xFF, 0xCC, 0x66),
    },
    "3: MIDNIGHT MOON": {
        "bg":         (0x1E, 0x22, 0x38),
        "unrevealed": (0x44, 0x4C, 0x6A),
        "revealed":   (0xC0, 0xC8, 0xDC),
        "bar":        (0x28, 0x2E, 0x48),
        "grid":       (0x35, 0x3B, 0x55),
        "hover":      (0x5A, 0x64, 0x84),
        "border_l":   (0x60, 0x68, 0x88),
        "border_d":   (0x2A, 0x30, 0x4A),
        "num1":       (0x88, 0xCC, 0xFF),
        "num2":       (0x77, 0xEE, 0xAA),
        "num3":       (0xFF, 0x77, 0x99),
        "num4":       (0xBB, 0x88, 0xFF),
        "exploded":   (0xFF, 0x44, 0x55),
        "win":        (0x88, 0xFF, 0xCC),
    },
    "4: CANDY POP": {
        "bg":         (0xF0, 0xE0, 0xF0),
        "unrevealed": (0xFF, 0x88, 0xAA),
        "revealed":   (0xFF, 0xF0, 0xF5),
        "bar":        (0xCC, 0x55, 0x88),
        "grid":       (0xCC, 0x55, 0x88),
        "hover":      (0xFF, 0xA0, 0xBB),
        "border_l":   (0xFF, 0xBB, 0xCC),
        "border_d":   (0xCC, 0x66, 0x88),
        "num1":       (0x44, 0x77, 0xEE),
        "num2":       (0x33, 0xAA, 0x55),
        "num3":       (0xEE, 0x33, 0x55),
        "num4":       (0x88, 0x44, 0xBB),
        "exploded":   (0xFF, 0x33, 0x55),
        "win":        (0xAA, 0xFF, 0xBB),
    },
}

CELL = 44
BORDER = 2
COLS = 5
ROWS = 4
PADDING = 30
THEME_W = COLS * CELL + 2
THEME_H = 30 + ROWS * CELL + 24 + 2
CARD_PAD = 20

W = CARD_PAD + 4 * (THEME_W + CARD_PAD)
H = 50 + THEME_H + 120 + CARD_PAD

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Theme Preview - Close window when done")

font_big = pygame.font.SysFont("Consolas", 20, bold=True)
font_sm = pygame.font.SysFont("Consolas", 13)
font_xs = pygame.font.SysFont("Consolas", 11)

def draw_raised(surf, rect, base, light, dark):
    pygame.draw.rect(surf, base, rect)
    x, y, w, h = rect
    for i in range(BORDER):
        pygame.draw.line(surf, light, (x+i, y+i), (x+w-1-i, y+i))
        pygame.draw.line(surf, light, (x+i, y+i), (x+i, y+h-1-i))
    for i in range(BORDER):
        pygame.draw.line(surf, dark, (x+i, y+h-1-i), (x+w-1-i, y+h-1-i))
        pygame.draw.line(surf, dark, (x+w-1-i, y+i), (x+w-1-i, y+h-1-i))

def draw_crescent_moon(surf, cx, cy, r):
    pygame.draw.circle(surf, (0xF0, 0xE8, 0xB0), (cx, cy), r)
    pygame.draw.circle(surf, (0x28, 0x2E, 0x48), (cx + r // 2, cy - r // 4), r)

def draw_preview(surf, ox, oy, name, t):
    pygame.draw.rect(surf, t["bar"], (ox, oy, THEME_W, 30))
    title = font_sm.render(name, True, (255,255,255))
    surf.blit(title, (ox + (THEME_W - title.get_width())//2, oy + 7))

    gy = oy + 30
    pygame.draw.rect(surf, t["bg"], (ox, gy, THEME_W, ROWS * CELL))

    mine_cells = {(0,3), (2,1), (3,4)}
    flag_cells = {(0,3)}
    revealed = {(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(1,3),(2,0),(2,2),(2,3),(2,4),(3,0),(3,1),(3,2),(3,3)}
    numbers = {(0,2):1, (1,2):2, (1,3):3, (2,0):1, (2,2):4, (2,4):2, (3,1):1, (3,2):1, (3,3):1}
    hover_cell = (0,4)

    for r in range(ROWS):
        for c in range(COLS):
            cx = ox + c * CELL
            cy = gy + r * CELL
            rect = pygame.Rect(cx, cy, CELL, CELL)

            if (r,c) in revealed:
                pygame.draw.rect(surf, t["revealed"], rect)
                if (r,c) in numbers:
                    n = numbers[(r,c)]
                    key = f"num{min(n,4)}"
                    ntxt = font_big.render(str(n), True, t[key])
                    surf.blit(ntxt, (cx + (CELL-ntxt.get_width())//2, cy + (CELL-ntxt.get_height())//2))
            elif (r,c) in flag_cells:
                draw_raised(surf, rect, t["unrevealed"], t["border_l"], t["border_d"])
                # draw small flag
                fx, fy = cx + CELL//2, cy + 8
                pygame.draw.line(surf, (0xDC,0x14,0x3C), (fx, fy), (fx, fy+CELL-18), 2)
                pygame.draw.polygon(surf, (0xDC,0x14,0x3C), [(fx, fy), (fx+10, fy+6), (fx, fy+12)])
            elif (r,c) == hover_cell:
                draw_raised(surf, rect, t["hover"], t["border_l"], t["border_d"])
            else:
                draw_raised(surf, rect, t["unrevealed"], t["border_l"], t["border_d"])

            pygame.draw.rect(surf, t["grid"], rect, 1)

    if "MIDNIGHT MOON" in name:
        moon_cx = ox + THEME_W - 30
        moon_cy = gy + 22
        draw_crescent_moon(surf, moon_cx, moon_cy, 12)

    # bottom bar
    by = gy + ROWS * CELL
    pygame.draw.rect(surf, t["bar"], (ox, by, THEME_W, 24))
    best = font_xs.render("BEST: 042S", True, (255,255,255))
    surf.blit(best, (ox + 6, by + 6))

def draw_swatch_row(surf, ox, oy, t, label, keys):
    lbl = font_xs.render(label, True, (200,200,200))
    surf.blit(lbl, (ox, oy))
    sx = ox
    for i, k in enumerate(keys):
        pygame.draw.rect(surf, t[k], (sx + i*22, oy + 16, 18, 18))
        pygame.draw.rect(surf, (80,80,80), (sx + i*22, oy + 16, 18, 18), 1)

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    title = font_big.render("MINESWEEPER THEME PREVIEW", True, (255,255,255))
    screen.blit(title, ((W - title.get_width())//2, 12))

    for i, (name, t) in enumerate(THEMES.items()):
        ox = CARD_PAD + i * (THEME_W + CARD_PAD)
        oy = 50

        # card background
        pygame.draw.rect(screen, (45,45,45), (ox-4, oy-4, THEME_W+8, THEME_H+8), border_radius=6)
        draw_preview(screen, ox, oy, name, t)

        # swatches below
        sy = oy + THEME_H + 14
        draw_swatch_row(screen, ox, sy, t, "Board:", ["bg","unrevealed","revealed","hover"])
        draw_swatch_row(screen, ox, sy + 42, t, "UI:", ["bar","border_l","border_d","grid"])
        draw_swatch_row(screen, ox, sy + 84, t, "Numbers:", ["num1","num2","num3","num4"])

    pygame.display.flip()

pygame.quit()
sys.exit()
