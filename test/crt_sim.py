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
plt.rcParams["font.size"] = 12

plt.close("all")
fig = plt.figure(figsize=(18, 10))
# 3 filas: (0) gráficas, (1) grilla presets, (2) controles
gs = fig.add_gridspec(3, 5, height_ratios=[3, 2, 2])

# Gráficas
ax_lat = fig.add_subplot(gs[0, 2])
ax_top = fig.add_subplot(gs[0, 3])
ax_scr = fig.add_subplot(gs[0, 4])

for ax in (ax_lat, ax_top, ax_scr):
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_aspect("equal")
    ax.set_facecolor("#111111"); ax.grid(True, color="#444444", alpha=0.5)

ax_lat.set_title("Vista lateral (deflexión vertical)")
ax_top.set_title("Vista superior (deflexión horizontal)")
ax_scr.set_title("Pantalla (Figuras de Lissajous)")
ax_scr.plot([-1,1,1,-1,-1], [-1,-1,1,1,-1], lw=1, alpha=0.6)

pt_lat, = ax_lat.plot([], [], "o", ms=8, color="orange")
pt_top, = ax_top.plot([], [], "o", ms=8, color="lime")
trail_scr, = ax_scr.plot([], [], lw=1.4, alpha=0.9, color="cyan")
hist_x, hist_y = [], []

# -------------------- GRID de presets --------------------
delta_labels = ["δ=0", "δ=π/4", "δ=π/2", "δ=3π/4", "δ=π"]
delta_values = [0.0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi]
ratios = [(1,1), (1,2), (1,3), (2,3)]
row_labels = ["1:1", "1:2", "1:3", "2:3"]

grid_parent = [fig.add_subplot(gs[1, i]) for i in range(5)]
for axp in grid_parent:
    axp.axis("off")

buttons = []
for r, (m,n) in enumerate(ratios):
    for c, delt in enumerate(delta_values):
        parent = grid_parent[c]
        y = 0.85 - r*0.2
        axb = parent.inset_axes([0.05, y, 0.90, 0.17])
        label = f"{row_labels[r]}  {delta_labels[c]}"
        
        b = Button(axb, label, color="#222222", hovercolor="#555555")
        b.label.set_color("white")  # o "cyan", "lime", etc.

        buttons.append((b, m, n, delt))

# -------------------- Panel de controles --------------------
ui1 = fig.add_subplot(gs[2, 0]); ui1.axis("off")
ui2 = fig.add_subplot(gs[2, 1]); ui2.axis("off")
ui3 = fig.add_subplot(gs[2, 2]); ui3.axis("off")
ui4 = fig.add_subplot(gs[2, 3]); ui4.axis("off")
ui5 = fig.add_subplot(gs[2, 4]); ui5.axis("off")

ax_mode = ui1.inset_axes([0.05, 0.50, 0.90, 0.45])
rb_mode = RadioButtons(ax_mode, ("manual", "sinusoidal"), active=1)
ax_vacc = ui2.inset_axes([0.10, 0.60, 0.80, 0.30])
ax_pers = ui2.inset_axes([0.10, 0.15, 0.80, 0.30])
s_vacc = Slider(ax_vacc, "V_acc (V)", 500.0, 4000.0, valinit=params["V_acc"])
s_pers = Slider(ax_pers, "Persistencia (s)", 0.05, 3.0, valinit=params["persist_s"])

ax_vx = ui3.inset_axes([0.10, 0.60, 0.80, 0.30])
ax_vy = ui3.inset_axes([0.10, 0.15, 0.80, 0.30])
s_vx = Slider(ax_vx, "Vx manual", -10.0, 10.0, valinit=params["Vx_manual"])
s_vy = Slider(ax_vy, "Vy manual", -10.0, 10.0, valinit=params["Vy_manual"])

ax_fx  = ui4.inset_axes([0.10, 0.70, 0.80, 0.22])
ax_fy  = ui4.inset_axes([0.10, 0.40, 0.80, 0.22])
ax_ax  = ui4.inset_axes([0.10, 0.10, 0.80, 0.22])
s_fx = Slider(ax_fx, "f_x (Hz)", 0.1, 10.0, valinit=params["fx"])
s_fy = Slider(ax_fy, "f_y (Hz)", 0.1, 10.0, valinit=params["fy"])
s_ax = Slider(ax_ax, "Amp X", 0.05, 1.0, valinit=params["Ax"])

ax_phx = ui5.inset_axes([0.10, 0.70, 0.80, 0.22])
ax_phy = ui5.inset_axes([0.10, 0.40, 0.80, 0.22])
ax_ay  = ui5.inset_axes([0.10, 0.10, 0.80, 0.22])
s_phx = Slider(ax_phx, "fase_x (rad)", -np.pi, np.pi, valinit=params["phx"])
s_phy = Slider(ax_phy, "fase_y (rad)", -np.pi, np.pi, valinit=params["phy"])
s_ay  = Slider(ax_ay,  "Amp Y", 0.05, 1.0, valinit=params["Ay"])

ax_reset = ui1.inset_axes([0.20, 0.05, 0.60, 0.35])
btn_reset = Button(ax_reset, "Resetear trazo",
                   color="#222222", hovercolor="#555555")
btn_reset.label.set_color("orange")  


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

for s in (s_vacc, s_pers, s_vx, s_vy, s_fx, s_fy, s_phx, s_phy, s_ax, s_ay):
    s.on_changed(on_change)
rb_mode.on_clicked(on_mode)

def on_reset(event):
    hist_x.clear(); hist_y.clear()
btn_reset.on_clicked(on_reset)

def apply_combo(m, n, delta):
    params["mode"] = "sinusoidal"; rb_mode.set_active(1)
    s_fx.set_val(float(m))
    s_fy.set_val(float(n))
    s_phx.set_val(0.0)
    s_phy.set_val(delta)
    s_ax.set_val(0.6); s_ay.set_val(0.6)

for b, m, n, d in buttons:
    b.on_clicked(lambda event, mm=m, nn=n, dd=d: apply_combo(mm, nn, dd))

# -------------------- Animación --------------------
def update(frame):
    t = frame * DT
    x, y = beam_pos(t, params)
    size = point_size_from_Vacc(params["V_acc"])
    pt_lat.set_data([0.0], [y]); pt_lat.set_markersize(size/10.0)
    pt_top.set_data([x], [0.0]); pt_top.set_markersize(size/10.0)
    hist_x.append(x); hist_y.append(y)
    maxlen = max(1, int(params["persist_s"] * FPS))
    if len(hist_x) > maxlen:
        hist_x[:] = hist_x[-maxlen:]
        hist_y[:] = hist_y[-maxlen:]
    trail_scr.set_data(hist_x, hist_y)
    return pt_lat, pt_top, trail_scr

ani = FuncAnimation(fig, update, interval=1000.0/FPS, blit=True)
fig.suptitle("Simulación Super Hiper Mega Impresionante de CRT - Grilla de presets (ωx:ωy × δ) + controles")
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
