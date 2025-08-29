# Modelo físico: geometría, step(dt,Vx,Vy,Va), impacto, persistencia
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Tuple
import time

@dataclass
class CRTModel:
    # Geometría abstracta (unidades arbitrarias pero consistentes)
    dist_canon_a_placas: float = 1.0
    largo_placas: float = 1.0
    dist_placas_a_pantalla: float = 2.0

    # Estado del electrón (posición y velocidad sobre eje z y deflexión x,y)
    # Usamos modelo *muy* simplificado: la deflexión es proporcional a Vx/Vy.
    x: float = 0.0
    y: float = 0.0

    # Persistencia (buffer de puntos normalizados y su tiempo)
    persist_ms: int = 500
    trail: Deque[Tuple[float, float, float]] = field(default_factory=deque)  # (x,y,ts)

    def set_persistence(self, tau_ms: int) -> None:
        self.persist_ms = max(0, tau_ms)

    def step(self, dt: float, Vx: float, Vy: float, Va: float) -> Tuple[float, float]:
        k = 0.8 / max(0.2, Va)  # más Va => menos deflexión (rayo más “duro”)
        self.x = max(-1.0, min(1.0, Vx * k))
        self.y = max(-1.0, min(1.0, Vy * k))

        # Persistencia: guardamos la traza con timestamp
        now = time.time()
        self.trail.append((self.x, self.y, now))
        # Podamos puntos viejos
        limit = now - (self.persist_ms / 1000.0)
        while self.trail and self.trail[0][2] < limit:
            self.trail.popleft()

        return self.x, self.y

    def impact_point(self) -> Tuple[float, float]:
        return self.x, self.y
