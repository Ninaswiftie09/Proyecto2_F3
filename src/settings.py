# (Opcional) Constantes: tamaños, límites de voltajes, colores, teclas

# Ventana
WIDTH = 960
HEIGHT = 640
FPS = 60

# Layout: 3 vistas (lateral, superior, pantalla)
# Zona izquierda: lateral (arriba) + superior (abajo) ; zona derecha: pantalla
PADDING = 12
SPLIT_X = int(WIDTH * 0.5)          # mitad izquierda / derecha
SPLIT_Y = int(HEIGHT * 0.5)         # mitad superior / inferior (solo lado izq)

# Rango de voltajes/valores por defecto
VA_DEFAULT = 1.0     # Voltaje de aceleración (escala abstracta)
V_MANUAL_STEP = 0.1  # Incremento para Vx/Vy manual
FREQ_STEP = 0.2      # Hz
PHASE_STEP = 0.1     # rad
AMP_STEP = 0.1
AMP_DEFAULT = 0.8
FREQ_DEFAULT = 1.0
PHASE_DEFAULT = 0.0

# Persistencia (ms)
PERSIST_MS_DEFAULT = 500
PERSIST_MS_MIN = 50
PERSIST_MS_MAX = 2000
PERSIST_STEP = 50
