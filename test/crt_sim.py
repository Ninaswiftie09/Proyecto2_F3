import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, RadioButtons, Button

# -------------------- Parámetros base --------------------
params = {
    "V_acc": 2000.0,
    "mode": "sinusoidal",
    "fx": 1.0, "fy": 1.0,
    "phx": 0.0, "phy": 0.0,
    "Ax": 0.6, "Ay": 0.6,
    "Vx_manual": 0.0, "Vy_manual": 0.0,
    "persist_s": 1.2,
    "amp_manual": 0.5,
}

FPS = 50
DT = 1.0 / FPS

def beam_pos(t, p):
    if p["mode"] == "sinusoidal":
        x = p["Ax"] * np.sin(2*np.pi*p["fx"]*t + p["phx"])
        y = p["Ay"] * np.sin(2*np.pi*p["fy"]*t + p["phy"])
    else:
        x = p["amp_manual"] * np.tanh(p["Vx_manual"]/5.0)
        y = p["amp_manual"] * np.tanh(p["Vy_manual"]/5.0)
    return x, y

def point_size_from_Vacc(Vacc):
    Vacc = np.clip(Vacc, 500.0, 4000.0)
    return 20 + 80 * (Vacc - 500.0) / 3500.0

plt.style.use("dark_background")
plt.rcParams.update({
    "font.size": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
})

plt.close("all")
fig = plt.figure(figsize=(16, 10))

# Layout: 3 filas, gráficas arriba, presets en medio, controles abajo
gs = fig.add_gridspec(4, 6, height_ratios=[0.3, 2.5, 1.2, 1.2], width_ratios=[1, 1, 1, 1, 1, 1])

# -------------------- Gráficas principales --------------------
ax_lat = fig.add_subplot(gs[1, 0:2])
ax_top = fig.add_subplot(gs[1, 2:4])
ax_scr = fig.add_subplot(gs[1, 4:6])

for ax in (ax_lat, ax_top, ax_scr):
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    ax.set_facecolor("#111111")
    ax.grid(True, color="#444444", alpha=0.5)

ax_lat.set_title("Vista lateral")
ax_top.set_title("Vista superior") 
ax_scr.set_title("Pantalla (Lissajous)")

# Dibujar pantalla
ax_scr.plot([-1,1,1,-1,-1], [-1,-1,1,1,-1], lw=1, alpha=0.6, color="white")

# Puntos y trazas
pt_lat, = ax_lat.plot([], [], "o", ms=6, color="orange")
pt_top, = ax_top.plot([], [], "o", ms=6, color="lime")
trail_scr, = ax_scr.plot([], [], lw=1.2, alpha=0.9, color="cyan")

hist_x, hist_y = [], []

# -------------------- Grid de presets compacto --------------------
delta_labels = ["δ=0", "δ=π/4", "δ=π/2", "δ=3π/4", "δ=π"]
delta_values = [0.0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi]
ratios = [(1,1), (1,2), (1,3), (2,3)]
ratio_labels = ["1:1", "1:2", "1:3", "2:3"]

# Crear grid de botones de presets más compacto
preset_ax = fig.add_subplot(gs[2, :])
preset_ax.axis("off")
preset_ax.set_title("Presets de figuras de Lissajous", fontsize=10, pad=15)

buttons = []
btn_width = 0.12
btn_height = 0.18
start_x = 0.05
start_y = 0.7

for r, (m, n) in enumerate(ratios):
    for c, delta in enumerate(delta_values):
        x_pos = start_x + c * (btn_width + 0.025)
        y_pos = start_y - r * (btn_height + 0.05)
        
        ax_btn = preset_ax.inset_axes([x_pos, y_pos, btn_width, btn_height])
        label = f"{ratio_labels[r]}\n{delta_labels[c]}"
        btn = Button(ax_btn, label, color="#333333", hovercolor="#555555")
        btn.label.set_fontsize(7)
        btn.label.set_color("white")
        buttons.append((btn, m, n, delta))

# -------------------- Controles compactos --------------------
# Fila inferior dividida en 6 secciones
control_axes = [fig.add_subplot(gs[3, i]) for i in range(6)]
for ax in control_axes:
    ax.axis("off")

# Sección 1: Modo y Reset
ax_mode = control_axes[0].inset_axes([0.05, 0.4, 0.9, 0.55])
rb_mode = RadioButtons(ax_mode, ("manual", "sinusoidal"), active=1)
for label in rb_mode.labels:
    label.set_fontsize(8)

ax_reset = control_axes[0].inset_axes([0.1, 0.05, 0.8, 0.25])
btn_reset = Button(ax_reset, "Limpiar", color="#444444", hovercolor="#666666")
btn_reset.label.set_fontsize(8)
btn_reset.label.set_color("orange")

# Sección 2: Voltaje y Persistencia
ax_vacc = control_axes[1].inset_axes([0.05, 0.55, 0.9, 0.35])
ax_pers = control_axes[1].inset_axes([0.05, 0.1, 0.9, 0.35])
s_vacc = Slider(ax_vacc, "V_acc", 500, 4000, valinit=params["V_acc"], valfmt="%.0f")
s_pers = Slider(ax_pers, "Persist", 0.05, 3.0, valinit=params["persist_s"], valfmt="%.1f")

# Sección 3: Control Manual
ax_vx = control_axes[2].inset_axes([0.05, 0.55, 0.9, 0.35])
ax_vy = control_axes[2].inset_axes([0.05, 0.1, 0.9, 0.35])
s_vx = Slider(ax_vx, "Vx", -10, 10, valinit=params["Vx_manual"], valfmt="%.1f")
s_vy = Slider(ax_vy, "Vy", -10, 10, valinit=params["Vy_manual"], valfmt="%.1f")

# Sección 4: Frecuencias
ax_fx = control_axes[3].inset_axes([0.05, 0.55, 0.9, 0.35])
ax_fy = control_axes[3].inset_axes([0.05, 0.1, 0.9, 0.35])
s_fx = Slider(ax_fx, "f_x", 0.1, 10, valinit=params["fx"], valfmt="%.1f")
s_fy = Slider(ax_fy, "f_y", 0.1, 10, valinit=params["fy"], valfmt="%.1f")

# Sección 5: Fases
ax_phx = control_axes[4].inset_axes([0.05, 0.55, 0.9, 0.35])
ax_phy = control_axes[4].inset_axes([0.05, 0.1, 0.9, 0.35])
s_phx = Slider(ax_phx, "φ_x", -np.pi, np.pi, valinit=params["phx"], valfmt="%.2f")
s_phy = Slider(ax_phy, "φ_y", -np.pi, np.pi, valinit=params["phy"], valfmt="%.2f")

# Sección 6: Amplitudes
ax_ax = control_axes[5].inset_axes([0.05, 0.55, 0.9, 0.35])
ax_ay = control_axes[5].inset_axes([0.05, 0.1, 0.9, 0.35])
s_ax = Slider(ax_ax, "A_x", 0.05, 1.0, valinit=params["Ax"], valfmt="%.2f")
s_ay = Slider(ax_ay, "A_y", 0.05, 1.0, valinit=params["Ay"], valfmt="%.2f")

# Ajustar tamaños de fuente para todos los sliders
for s in (s_vacc, s_pers, s_vx, s_vy, s_fx, s_fy, s_phx, s_phy, s_ax, s_ay):
    s.label.set_fontsize(7)
    s.valtext.set_fontsize(7)

# Títulos para las secciones de control
control_titles = ["Modo", "Sistema", "Manual", "Frecuencias", "Fases", "Amplitudes"]
for i, title in enumerate(control_titles):
    control_axes[i].text(0.5, 0.95, title, ha='center', va='top', 
                        fontsize=9, fontweight='bold', transform=control_axes[i].transAxes)

# -------------------- Callbacks --------------------
def on_mode(label):
    params["mode"] = label

def on_change(_=None):
    params["V_acc"] = s_vacc.val
    params["persist_s"] = s_pers.val
    params["Vx_manual"] = s_vx.val
    params["Vy_manual"] = s_vy.val
    params["fx"] = s_fx.val
    params["fy"] = s_fy.val
    params["phx"] = s_phx.val
    params["phy"] = s_phy.val
    params["Ax"] = s_ax.val
    params["Ay"] = s_ay.val

# Conectar callbacks
for s in (s_vacc, s_pers, s_vx, s_vy, s_fx, s_fy, s_phx, s_phy, s_ax, s_ay):
    s.on_changed(on_change)

rb_mode.on_clicked(on_mode)

def on_reset(event):
    hist_x.clear()
    hist_y.clear()

btn_reset.on_clicked(on_reset)

def apply_combo(m, n, delta):
    params["mode"] = "sinusoidal"
    rb_mode.set_active(1)
    s_fx.set_val(float(m))
    s_fy.set_val(float(n))
    s_phx.set_val(0.0)
    s_phy.set_val(delta)
    s_ax.set_val(0.6)
    s_ay.set_val(0.6)

# Conectar botones de presets
for btn, m, n, d in buttons:
    btn.on_clicked(lambda event, mm=m, nn=n, dd=d: apply_combo(mm, nn, dd))

# -------------------- Animación --------------------
def update(frame):
    t = frame * DT
    x, y = beam_pos(t, params)
    
    size = point_size_from_Vacc(params["V_acc"])
    pt_lat.set_data([0.0], [y])
    pt_lat.set_markersize(size/15.0)
    pt_top.set_data([x], [0.0])
    pt_top.set_markersize(size/15.0)
    
    hist_x.append(x)
    hist_y.append(y)
    
    maxlen = max(1, int(params["persist_s"] * FPS))
    if len(hist_x) > maxlen:
        hist_x[:] = hist_x[-maxlen:]
        hist_y[:] = hist_y[-maxlen:]
    
    trail_scr.set_data(hist_x, hist_y)
    return pt_lat, pt_top, trail_scr

ani = FuncAnimation(fig, update, interval=1000.0/FPS, blit=True)

fig.suptitle("Simulador CRT - Figuras de Lissajous", fontsize=12, y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()