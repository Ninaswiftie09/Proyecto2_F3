# Generadores de señal: ManualSignal, SineSignal (freq, phase, amp)
import math
from dataclasses import dataclass

@dataclass
class ManualSignal:
    value: float = 0.0
    def get(self, t: float) -> float:
        return self.value

@dataclass
class SineSignal:
    freq: float = 1.0     # Hz
    phase: float = 0.0    # rad
    amp: float = 1.0
    def get(self, t: float) -> float:
        return self.amp * math.sin(2 * math.pi * self.freq * t + self.phase)

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))
