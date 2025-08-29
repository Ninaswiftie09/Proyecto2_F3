 # Punto de entrada. Bucle principal, orquestación (signals->core->ui)
import pygame, sys, time
from settings import *
from crt_core import CRTModel
from signals import ManualSignal, SineSignal, clamp
import ui

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CRT Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    # Estado
    mode = "MANUAL"  # or "SINE"
    Va = VA_DEFAULT
    Vx_manual = 0.0
    Vy_manual = 0.0

    # Señales
    sigX_manual = ManualSignal(0.0)
    sigY_manual = ManualSignal(0.0)
    sigX_sine = SineSignal(FREQ_DEFAULT, PHASE_DEFAULT, AMP_DEFAULT)
    sigY_sine = SineSignal(FREQ_DEFAULT, PHASE_DEFAULT, AMP_DEFAULT)

    # Modelo
    crt = CRTModel(persist_ms=PERSIST_MS_DEFAULT)

    start_t = time.time()
    running = True
    fps_val = FPS

    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        t = now - start_t

        # --- Eventos / Controles ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    mode = "SINE" if mode == "MANUAL" else "MANUAL"
                elif e.key == pygame.K_1:
                    Va = max(0.2, Va - 0.1)
                elif e.key == pygame.K_2:
                    Va += 0.1
                elif e.key == pygame.K_t:
                    crt.set_persistence(max(PERSIST_MS_MIN, crt.persist_ms - PERSIST_STEP))
                elif e.key == pygame.K_g:
                    crt.set_persistence(min(PERSIST_MS_MAX, crt.persist_ms + PERSIST_STEP))

        keys = pygame.key.get_pressed()
        if mode == "MANUAL":
            # Vx/Vy manual con WASD
            if keys[pygame.K_a]: Vx_manual -= V_MANUAL_STEP * dt * 8
            if keys[pygame.K_d]: Vx_manual += V_MANUAL_STEP * dt * 8
            if keys[pygame.K_w]: Vy_manual += V_MANUAL_STEP * dt * 8
            if keys[pygame.K_s]: Vy_manual -= V_MANUAL_STEP * dt * 8
            Vx_manual = clamp(Vx_manual, -1.0, 1.0)
            Vy_manual = clamp(Vy_manual, -1.0, 1.0)
            sigX_manual.value = Vx_manual
            sigY_manual.value = Vy_manual
        else:
            # Ajustes senoidales
            if keys[pygame.K_LEFT]:  sigX_sine.freq = max(0.1, sigX_sine.freq - FREQ_STEP * dt * 5)
            if keys[pygame.K_RIGHT]: sigX_sine.freq += FREQ_STEP * dt * 5
            if keys[pygame.K_DOWN]:  sigY_sine.freq = max(0.1, sigY_sine.freq - FREQ_STEP * dt * 5)
            if keys[pygame.K_UP]:    sigY_sine.freq += FREQ_STEP * dt * 5
            if keys[pygame.K_q]:     sigX_sine.phase -= PHASE_STEP * dt * 8
            if keys[pygame.K_e]:     sigX_sine.phase += PHASE_STEP * dt * 8
            if keys[pygame.K_z]:
                sigX_sine.amp = max(0.1, sigX_sine.amp - AMP_STEP * dt * 8)
                sigY_sine.amp = max(0.1, sigY_sine.amp - AMP_STEP * dt * 8)
            if keys[pygame.K_x]:
                sigX_sine.amp += AMP_STEP * dt * 8
                sigY_sine.amp += AMP_STEP * dt * 8

        # --- Señales actuales ---
        if mode == "MANUAL":
            Vx = sigX_manual.get(t)
            Vy = sigY_manual.get(t)
        else:
            Vx = sigX_sine.get(t)
            Vy = sigY_sine.get(t)

        # --- Update físico ---
        point = crt.step(dt, Vx, Vy, Va)

        # --- Dibujar ---
        ui.draw(
            screen=screen,
            font=font,
            now=now,
            point_xy=point,
            trail=crt.trail,
            params_hud={
                "mode": mode,
                "Va": Va, "Vx": Vx, "Vy": Vy,
                "fx": sigX_sine.freq, "fy": sigY_sine.freq,
                "phase": sigX_sine.phase, "amp": sigX_sine.amp,
                "persist_ms": crt.persist_ms,
                "fps": fps_val
            },
            cfg={"WIDTH": WIDTH, "HEIGHT": HEIGHT, "PADDING": PADDING, "SPLIT_X": SPLIT_X, "SPLIT_Y": SPLIT_Y},
        )

        pygame.display.flip()
        fps_val = 0.9*fps_val + 0.1*clock.get_fps()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
