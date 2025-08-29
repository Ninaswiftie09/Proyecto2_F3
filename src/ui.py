# Render e interfaz: 3 vistas (lateral, superior, pantalla), HUD, inputs
import pygame
from typing import Tuple, Deque
import time

def _rects_layout(W: int, H: int, PADDING: int, SPLIT_X: int, SPLIT_Y: int):
    left = pygame.Rect(PADDING, PADDING, SPLIT_X - 2*PADDING, H - 2*PADDING)
    right = pygame.Rect(SPLIT_X + PADDING, PADDING, W - SPLIT_X - 2*PADDING, H - 2*PADDING)
    # dentro de left: top/bottom
    top = pygame.Rect(left.x, left.y, left.w, (left.h - PADDING)//2 - PADDING//2)
    bottom = pygame.Rect(left.x, top.bottom + PADDING, left.w, left.h - top.h - PADDING)
    return top, bottom, right

def draw(
    screen: pygame.Surface,
    font: pygame.font.Font,
    now: float,
    point_xy: Tuple[float, float],
    trail: Deque[Tuple[float, float, float]],
    params_hud: dict,
    cfg: dict,
):
    screen.fill((15, 17, 22))
    top, bottom, right = _rects_layout(cfg["WIDTH"], cfg["HEIGHT"], cfg["PADDING"], cfg["SPLIT_X"], cfg["SPLIT_Y"])

    # Marcos
    pygame.draw.rect(screen, (70, 70, 80), top, 2)     # Lateral
    pygame.draw.rect(screen, (70, 70, 80), bottom, 2)  # Superior
    pygame.draw.rect(screen, (120, 120, 130), right, 2)  # Pantalla

    # Etiquetas
    _label(screen, font, "Vista lateral", (top.x+8, top.y+6))
    _label(screen, font, "Vista superior", (bottom.x+8, bottom.y+6))
    _label(screen, font, "Pantalla (frontal)", (right.x+8, right.y+6))

    # Punto en pantalla (normalizado [-1,1] -> a pixeles del rect 'right')
    _draw_screen(screen, right, point_xy, trail, now, params_hud["persist_ms"])

    # HUD
    lines = [
        f"Modo: {params_hud['mode']}",
        f"Va={params_hud['Va']:.2f}  Vx={params_hud['Vx']:.2f}  Vy={params_hud['Vy']:.2f}",
        f"freqX={params_hud['fx']:.2f}  freqY={params_hud['fy']:.2f}",
        f"phase={params_hud['phase']:.2f}  amp={params_hud['amp']:.2f}",
        f"persist={params_hud['persist_ms']} ms   FPS~{params_hud['fps']:.0f}",
        "Controles: M modo | WASD Vx/Vy | 1/2 Va | ←/→ fx | ↓/↑ fy | Q/E phase | Z/X amp | T/G persist",
    ]
    _hud(screen, font, lines, (8, cfg["HEIGHT"] - 18*len(lines) - 8))

def _label(screen, font, text, pos):
    surf = font.render(text, True, (180, 180, 200))
    screen.blit(surf, pos)

def _hud(screen, font, lines, pos):
    x, y = pos
    for ln in lines:
        surf = font.render(ln, True, (210, 210, 220))
        screen.blit(surf, (x, y))
        y += 18

def _draw_screen(screen, rect, point_xy, trail, now, persist_ms):
    # Traza con persistencia (puntos viejos más transparentes)
    for x, y, ts in trail:
        age = now - ts
        a = max(0.0, 1.0 - age / (persist_ms / 1000.0))
        col = (int(40 + 180*a), int(200*a), int(60*a))  # verde con “fade”
        px = int(rect.x + (x*0.5 + 0.5) * rect.w)
        py = int(rect.y + (-(y)*0.5 + 0.5) * rect.h)    # y invertida para pantalla
        screen.fill(col, (px-1, py-1, 3, 3))

    # Punto actual (más brillante)
    x, y = point_xy
    px = int(rect.x + (x*0.5 + 0.5) * rect.w)
    py = int(rect.y + (-(y)*0.5 + 0.5) * rect.h)
    screen.fill((120, 255, 120), (px-2, py-2, 5, 5))
