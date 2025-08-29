import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, RadioButtons, Button

plt.style.use("dark_background")

m_e = 9.109e-31
q_e = -1.602e-19
D_vert = 0.05
D_horiz = 0.05
L_screen = 0.50

params = {
    "V_acc": 2000.0,
    "Vx_manual": 0.0,
    "Vy_manual": 0.0,
    "mode": "sinusoid",
    "fx": 2.0,
    "fy": 3.0,
    "phx": 0.0,
    "phy": np.pi/2,
    "persist_s": 0.6,
    "amp_manual": 0.5,
    "amp_sine": 0.5,
}

FPS = 50
DT = 1.0 / FPS

def beam_pos(t, p):
    if p["mode"] == "sinusoid":
        x = p["amp_sine"] * np.sin(2*np.pi*p["fx"]*t + p["phx"])
        y = p["amp_sine"] * np.sin(2*np.pi*p["fy"]*t + p["phy"])
    else:
        x = p["amp_manual"] * np.tanh(p["Vx_manual"] / 5.0)
        y = p["amp_manual"] * np.tanh(p["Vy_manual"] / 5.0)
    return x, y

def point_size_from_Vacc(Vacc):
    Vacc = np.clip(Vacc, 500.0, 4000.0)
    return 20 + 80 * (Vacc - 500.0) / (3500.0)

plt.close("all")
fig = plt.figure(figsize=(12, 7))
gs = fig.add_gridspec(2, 3, height_ratios=[3, 1])

ax_lat = fig.add_subplot(gs[0, 0])
ax_top = fig.add_subplot(gs[0, 1])
ax_scr = fig.add_subplot(gs[0, 2])

ui_ax = [
    fig.add_subplot(gs[1, 0]),
    fig.add_subplot(gs[1, 1]),
    fig.add_subplot(gs[1, 2]),
]

for ax in (ax_lat, ax_top, ax_scr):
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-1.0, 1.0)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)

ax_lat.set_title("Vista lateral (deflexion vertical)")
ax_top.set_title("Vista superior (deflexion horizontal)")
ax_scr.set_title("Pantalla (Figuras de Lissajous)")

plate_lat_y = 0.7
ax_lat.hlines([ plate_lat_y, -plate_lat_y ], xmin=-0.3, xmax=0.3, linestyles="--", alpha=0.3)
ax_lat.vlines([ -0.3, 0.3 ], ymin=-plate_lat_y, ymax=plate_lat_y, linestyles=":", alpha=0.2)

plate_top_x = 0.7
ax_top.vlines([ plate_top_x, -plate_top_x ], ymin=-0.3, ymax=0.3, linestyles="--", alpha=0.3)
ax_top.hlines([ -0.3, 0.3 ], xmin=-plate_top_x, xmax=plate_top_x, linestyles=":", alpha=0.2)

ax_scr.plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], lw=1, alpha=0.4)

pt_lat, = ax_lat.plot([], [], marker="o", ls="", ms=8)
pt_top, = ax_top.plot([], [], marker="o", ls="", ms=8)
trail_scr, = ax_scr.plot([], [], lw=1, alpha=0.8)

hist_x, hist_y, hist_t = [], [], []

ax_mode = ui_ax[0].inset_axes([0.02, 0.55, 0.4, 0.35])
ax_vacc = ui_ax[0].inset_axes([0.5, 0.65, 0.45, 0.25])
ax_persist = ui_ax[0].inset_axes([0.5, 0.15, 0.45, 0.25])

rb_mode = RadioButtons(ax_mode, ("manual", "sinusoid"), active=1)
s_vacc = Slider(ax_vacc, "V_acc (V)", 500.0, 4000.0, valinit=params["V_acc"])
s_persist = Slider(ax_persist, "Persist (s)", 0.05, 3.0, valinit=params["persist_s"])

ui_ax[0].axis("off")

ax_vx = ui_ax[1].inset_axes([0.1, 0.55, 0.8, 0.3])
ax_vy = ui_ax[1].inset_axes([0.1, 0.15, 0.8, 0.3])
s_vx = Slider(ax_vx, "Vx manual", -10.0, 10.0, valinit=params["Vx_manual"])
s_vy = Slider(ax_vy, "Vy manual", -10.0, 10.0, valinit=params["Vy_manual"])
ui_ax[1].axis("off")

ax_fx = ui_ax[2].inset_axes([0.05, 0.65, 0.4, 0.25])
ax_fy = ui_ax[2].inset_axes([0.55, 0.65, 0.4, 0.25])
ax_phx = ui_ax[2].inset_axes([0.05, 0.25, 0.4, 0.25])
ax_phy = ui_ax[2].inset_axes([0.55, 0.25, 0.4, 0.25])
ax_reset = ui_ax[2].inset_axes([0.35, 0.02, 0.3, 0.18])

s_fx = Slider(ax_fx, "fx (Hz)", 0.1, 10.0, valinit=params["fx"])
s_fy = Slider(ax_fy, "fy (Hz)", 0.1, 10.0, valinit=params["fy"])
s_phx = Slider(ax_phx, "phx (rad)", -np.pi, np.pi, valinit=params["phx"])
s_phy = Slider(ax_phy, "phy (rad)", -np.pi, np.pi, valinit=params["phy"])
btn_reset = Button(ax_reset, "Resetear")

ui_ax[2].axis("off")

def on_mode(label):
    params["mode"] = label

def on_change_val(_):
    params["V_acc"] = s_vacc.val
    params["persiste_s"] = s_persist.val
    params["Vx_manual"] = s_vx.val
    params["Vy_manual"] = s_vy.val
    params["fx"] = s_fx.val
    params["fy"] = s_fy.val
    params["phx"] = s_phx.val
    params["phy"] = s_phy.val

def on_reset(event):
    del hist_x[:]
    del hist_y[:]
    del hist_t[:]

rb_mode.on_clicked(on_mode)
for s in (s_vacc, s_persist, s_vx, s_vy, s_fx, s_fy, s_phx, s_phy):
    s.on_changed(on_change_val)
btn_reset.on_clicked(on_reset)

t0 = 0.0
def update(frame):
    global t0
    t = t0 + frame * DT
    x = None; y = None
    if params["mode"] == "sinusoid":
        x = params["amp_sine"] * np.sin(2*np.pi*params["fx"]*t + params["phx"])
        y = params["amp_sine"] * np.sin(2*np.pi*params["fy"]*t + params["phy"])
    else:
        x = params["amp_manual"] * np.tanh(params["Vx_manual"] / 5.0)
        y = params["amp_manual"] * np.tanh(params["Vy_manual"] / 5.0)

    size = point_size_from_Vacc(params["V_acc"])
    pt_lat.set_data([0.0], [y])
    pt_lat.set_markersize(size/10.0)
    pt_top.set_data([x], [0.0])
    pt_top.set_markersize(size/10.0)

    hist_x.append(x); hist_y.append(y); hist_t.append(t)
    while hist_t and (t - hist_t[0]) > params["persist_s"]:
        hist_x.pop(0); hist_y.pop(0); hist_t.pop(0)

    trail_scr.set_data(hist_x, hist_y)
    return pt_lat, pt_top, trail_scr

ani = FuncAnimation(fig, update, interval=1000.0/FPS, blit=True)

fig.suptitle("SUPER HIPER MEGA SIMULACION CRT")

plt.tight_layout()
plt.show()
