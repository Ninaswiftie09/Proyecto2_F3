import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, RadioButtons, Button

# -------------------- Constantes físicas y geometría del CRT --------------------
# Constantes fundamentales
m_e = 9.109e-31  # masa del electrón [kg]
q_e = -1.602e-19  # carga del electrón [C]

# Geometría del CRT (en metros)
L_gun_to_plates = 0.02     # distancia cañón → entrada de placas
L_plates = 0.05            # largo de las placas deflectoras
L_plates_to_screen = 0.25  # distancia salida placas → pantalla
L_total = L_gun_to_plates + L_plates + L_plates_to_screen  # distancia total
D_plates_x = 0.02          # separación placas horizontales (deflexión X)
D_plates_y = 0.02          # separación placas verticales (deflexión Y)
screen_size = 0.15         # tamaño de pantalla (±screen_size/2)

# -------------------- Parámetros de control --------------------
params = {
    "V_acc": 2000.0,          # voltaje acelerador [V]
    "mode": "sinusoidal",     # modo de operación
    "fx": 1.0, "fy": 1.0,     # frecuencias [Hz]
    "phx": 0.0, "phy": 0.0,   # fases [rad]
    "Vx": 50.0, "Vy": 50.0,   # voltajes deflexión [V]
    "Vx_manual": 0.0, "Vy_manual": 0.0,  # control manual [V]
    "persist_s": 1.2,         # persistencia del trazo [s]
}

FPS = 60
DT = 1.0 / FPS

def calculate_electron_trajectory(t, p):
    """Calcula la trayectoria real del electrón considerando la física del CRT"""
    
    # Velocidad inicial del electrón (aceleración por Va)
    v0 = np.sqrt(2 * abs(q_e) * p["V_acc"] / m_e)  # [m/s]
    
    # Determinar voltajes de deflexión según el modo
    if p["mode"] == "sinusoidal":
        Vx_t = p["Vx"] * np.sin(2*np.pi*p["fx"]*t + p["phx"])
        Vy_t = p["Vy"] * np.sin(2*np.pi*p["fy"]*t + p["phy"])
    else:
        Vx_t = p["Vx_manual"]
        Vy_t = p["Vy_manual"]
    
    # Campos eléctricos en las placas deflectoras
    Ex = Vx_t / D_plates_x  # [V/m]
    Ey = Vy_t / D_plates_y  # [V/m]
    
    # Aceleraciones en las regiones de deflexión
    ax = q_e * Ex / m_e  # [m/s²]
    ay = q_e * Ey / m_e  # [m/s²]
    
    # Tiempo para atravesar las placas
    t_plates = L_plates / v0
    
    # Deflexión dentro de las placas (cinemática)
    delta_x_plates = 0.5 * ax * t_plates**2
    delta_y_plates = 0.5 * ay * t_plates**2
    
    # Velocidades al salir de las placas
    vx_exit = ax * t_plates
    vy_exit = ay * t_plates
    
    # Tiempo para llegar a la pantalla después de las placas
    t_screen = L_plates_to_screen / v0
    
    # Deflexión adicional en el espacio libre
    delta_x_free = vx_exit * t_screen
    delta_y_free = vy_exit * t_screen
    
    # Posición final en la pantalla
    x_screen = delta_x_plates + delta_x_free
    y_screen = delta_y_plates + delta_y_free
    
    # Normalizar para visualización (convertir a unidades de pantalla)
    x_norm = np.clip(x_screen / (screen_size/2), -1.0, 1.0)
    y_norm = np.clip(y_screen / (screen_size/2), -1.0, 1.0)
    
    # Calcular trayectoria completa para las vistas laterales
    # Posiciones en Z
    z1 = L_gun_to_plates  # entrada a placas
    z2 = L_gun_to_plates + L_plates  # salida de placas
    z3 = L_total  # pantalla
    
    # Trayectoria en las placas (parábola)
    z_plates = np.linspace(z1, z2, 20)
    t_local = (z_plates - z1) / v0
    x_plates = 0.5 * ax * t_local**2
    y_plates = 0.5 * ay * t_local**2
    
    # Trayectoria en espacio libre (línea recta)
    z_free = np.linspace(z2, z3, 20)
    x_free = delta_x_plates + vx_exit * (z_free - z2) / v0
    y_free = delta_y_plates + vy_exit * (z_free - z2) / v0
    
    # Combinar trayectorias
    z_total = np.concatenate([z_plates, z_free])
    x_total = np.concatenate([x_plates, x_free])
    y_total = np.concatenate([y_plates, y_free])
    
    # Normalizar para visualización
    z_norm = z_total / L_total * 2 - 1  # [-1, 1]
    x_traj_norm = x_total / (screen_size/2)
    y_traj_norm = y_total / (screen_size/2)
    
    return x_norm, y_norm, z_norm, x_traj_norm, y_traj_norm

def beam_intensity(V_acc):
    """Intensidad del haz basada en el voltaje acelerador"""
    V_acc = np.clip(V_acc, 500.0, 4000.0)
    return 0.3 + 0.7 * (V_acc - 500.0) / 3500.0

plt.style.use("dark_background")
plt.rcParams.update({
    "font.size": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
})

plt.close("all")
fig = plt.figure(figsize=(15, 9))

# Layout: gráficas arriba, presets en medio, controles abajo
gs = fig.add_gridspec(4, 6, height_ratios=[0.2, 2.0, 1.0, 1.0], width_ratios=[1, 1, 1, 1, 1, 1])

# -------------------- Gráficas principales --------------------
ax_lat = fig.add_subplot(gs[1, 0:2])  # Vista lateral (Z vs Y)
ax_top = fig.add_subplot(gs[1, 2:4])  # Vista superior (Z vs X)
ax_scr = fig.add_subplot(gs[1, 4:6])  # Pantalla

# Configuración de ejes
ax_lat.set_xlim(-1, 1)
ax_lat.set_ylim(-1, 1)
ax_lat.set_xlabel("Posición Z (normalizada)")
ax_lat.set_ylabel("Deflexión Y")
ax_lat.set_title("Vista Lateral (Z vs Y)")
ax_lat.grid(True, alpha=0.3)

ax_top.set_xlim(-1, 1)
ax_top.set_ylim(-1, 1)
ax_top.set_xlabel("Posición Z (normalizada)")
ax_top.set_ylabel("Deflexión X")
ax_top.set_title("Vista Superior (Z vs X)")
ax_top.grid(True, alpha=0.3)

ax_scr.set_xlim(-1, 1)
ax_scr.set_ylim(-1, 1)
ax_scr.set_xlabel("X")
ax_scr.set_ylabel("Y")
ax_scr.set_title("Pantalla CRT")
ax_scr.set_aspect("equal")
ax_scr.grid(True, alpha=0.3)

# Dibujar geometría del CRT en vistas laterales
# Placas deflectoras
plate_start = (L_gun_to_plates / L_total * 2 - 1)
plate_end = ((L_gun_to_plates + L_plates) / L_total * 2 - 1)

# Placas verticales (vista lateral)
ax_lat.axvspan(plate_start, plate_end, alpha=0.2, color='yellow', label='Placas deflectoras')
ax_lat.hlines([0.8, -0.8], plate_start, plate_end, colors='orange', linestyles='--', alpha=0.7, linewidth=2)

# Placas horizontales (vista superior)
ax_top.axvspan(plate_start, plate_end, alpha=0.2, color='yellow')
ax_top.hlines([0.8, -0.8], plate_start, plate_end, colors='orange', linestyles='--', alpha=0.7, linewidth=2)

# Pantalla
screen_z = 1.0
ax_lat.axvline(screen_z, color='white', linewidth=3, alpha=0.8, label='Pantalla')
ax_top.axvline(screen_z, color='white', linewidth=3, alpha=0.8)

# Cañón de electrones
ax_lat.axvline(-1.0, color='red', linewidth=2, alpha=0.8, label='Cañón')
ax_top.axvline(-1.0, color='red', linewidth=2, alpha=0.8)

ax_lat.legend(fontsize=7, loc='upper left')

# Marco de la pantalla
ax_scr.plot([-1,1,1,-1,-1], [-1,-1,1,1,-1], lw=2, alpha=0.8, color="white")

# Elementos gráficos animados
traj_lat, = ax_lat.plot([], [], 'cyan', linewidth=2, alpha=0.8)
traj_top, = ax_top.plot([], [], 'lime', linewidth=2, alpha=0.8)
pt_lat, = ax_lat.plot([], [], 'o', ms=8, color="cyan")
pt_top, = ax_top.plot([], [], 'o', ms=8, color="lime")
trail_scr, = ax_scr.plot([], [], lw=1.5, alpha=0.9, color="yellow")

hist_x, hist_y = [], []

# -------------------- Grid de presets --------------------
delta_labels = ["δ=0", "δ=π/4", "δ=π/2", "δ=3π/4", "δ=π"]
delta_values = [0.0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi]
ratios = [(1,1), (1,2), (1,3), (2,3)]
ratio_labels = ["1:1", "1:2", "1:3", "2:3"]

preset_ax = fig.add_subplot(gs[2, :])
preset_ax.axis("off")
preset_ax.set_title("Presets de figuras de Lissajous", fontsize=9, pad=5)

buttons = []
btn_width = 0.11
btn_height = 0.35
start_x = 0.05
start_y = 0.6

for r, (m, n) in enumerate(ratios):
    for c, delta in enumerate(delta_values):
        x_pos = start_x + c * (btn_width + 0.025)
        y_pos = start_y - r * (btn_height + 0.08)
        
        ax_btn = preset_ax.inset_axes([x_pos, y_pos, btn_width, btn_height])
        label = f"{ratio_labels[r]}\n{delta_labels[c]}"
        btn = Button(ax_btn, label, color="#333333", hovercolor="#555555")
        btn.label.set_fontsize(7)
        btn.label.set_color("white")
        buttons.append((btn, m, n, delta))

# -------------------- Controles --------------------
control_axes = [fig.add_subplot(gs[3, i]) for i in range(6)]
for ax in control_axes:
    ax.axis("off")

# Sección 1: Modo y Reset
ax_mode = control_axes[0].inset_axes([0.05, 0.35, 0.9, 0.6])
rb_mode = RadioButtons(ax_mode, ("manual", "sinusoidal"), active=1)
for label in rb_mode.labels:
    label.set_fontsize(7)

ax_reset = control_axes[0].inset_axes([0.1, 0.05, 0.8, 0.25])
btn_reset = Button(ax_reset, "Limpiar", color="#444444", hovercolor="#666666")
btn_reset.label.set_fontsize(7)
btn_reset.label.set_color("orange")

# Sección 2: Voltajes del sistema
ax_vacc = control_axes[1].inset_axes([0.05, 0.5, 0.9, 0.4])
ax_pers = control_axes[1].inset_axes([0.05, 0.05, 0.9, 0.4])
s_vacc = Slider(ax_vacc, "V_acc (V)", 500, 4000, valinit=params["V_acc"], valfmt="%.0f")
s_pers = Slider(ax_pers, "Persist (s)", 0.05, 3.0, valinit=params["persist_s"], valfmt="%.1f")

# Sección 3: Control Manual
ax_vx_man = control_axes[2].inset_axes([0.05, 0.5, 0.9, 0.4])
ax_vy_man = control_axes[2].inset_axes([0.05, 0.05, 0.9, 0.4])
s_vx_man = Slider(ax_vx_man, "Vx (V)", -200, 200, valinit=params["Vx_manual"], valfmt="%.0f")
s_vy_man = Slider(ax_vy_man, "Vy (V)", -200, 200, valinit=params["Vy_manual"], valfmt="%.0f")

# Sección 4: Frecuencias
ax_fx = control_axes[3].inset_axes([0.05, 0.5, 0.9, 0.4])
ax_fy = control_axes[3].inset_axes([0.05, 0.05, 0.9, 0.4])
s_fx = Slider(ax_fx, "f_x (Hz)", 0.1, 10, valinit=params["fx"], valfmt="%.1f")
s_fy = Slider(ax_fy, "f_y (Hz)", 0.1, 10, valinit=params["fy"], valfmt="%.1f")

# Sección 5: Fases
ax_phx = control_axes[4].inset_axes([0.05, 0.5, 0.9, 0.4])
ax_phy = control_axes[4].inset_axes([0.05, 0.05, 0.9, 0.4])
s_phx = Slider(ax_phx, "φ_x (rad)", -np.pi, np.pi, valinit=params["phx"], valfmt="%.2f")
s_phy = Slider(ax_phy, "φ_y (rad)", -np.pi, np.pi, valinit=params["phy"], valfmt="%.2f")

# Sección 6: Amplitudes de voltaje
ax_vx = control_axes[5].inset_axes([0.05, 0.5, 0.9, 0.4])
ax_vy = control_axes[5].inset_axes([0.05, 0.05, 0.9, 0.4])
s_vx = Slider(ax_vx, "Vx_amp (V)", 0, 200, valinit=params["Vx"], valfmt="%.0f")
s_vy = Slider(ax_vy, "Vy_amp (V)", 0, 200, valinit=params["Vy"], valfmt="%.0f")

# Ajustar tamaños de fuente
for s in (s_vacc, s_pers, s_vx_man, s_vy_man, s_fx, s_fy, s_phx, s_phy, s_vx, s_vy):
    s.label.set_fontsize(7)
    s.valtext.set_fontsize(7)

# Títulos de secciones
control_titles = ["Modo", "Sistema", "Manual", "Frecuencias", "Fases", "Voltajes"]
for i, title in enumerate(control_titles):
    control_axes[i].text(0.5, 0.98, title, ha='center', va='top', 
                        fontsize=8, fontweight='bold', transform=control_axes[i].transAxes)

# Mostrar parámetros físicos
info_text = f"CRT Geometry:\nL_total = {L_total*1000:.0f} mm\nD_plates = {D_plates_x*1000:.0f} mm\nScreen = {screen_size*1000:.0f} mm"
fig.text(0.02, 0.02, info_text, fontsize=7, color='cyan', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))

# -------------------- Callbacks --------------------
def on_mode(label):
    params["mode"] = label

def on_change(_=None):
    params["V_acc"] = s_vacc.val
    params["persist_s"] = s_pers.val
    params["Vx_manual"] = s_vx_man.val
    params["Vy_manual"] = s_vy_man.val
    params["fx"] = s_fx.val
    params["fy"] = s_fy.val
    params["phx"] = s_phx.val
    params["phy"] = s_phy.val
    params["Vx"] = s_vx.val
    params["Vy"] = s_vy.val

# Conectar callbacks
for s in (s_vacc, s_pers, s_vx_man, s_vy_man, s_fx, s_fy, s_phx, s_phy, s_vx, s_vy):
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
    s_vx.set_val(100.0)
    s_vy.set_val(100.0)

# Conectar botones de presets
for btn, m, n, d in buttons:
    btn.on_clicked(lambda event, mm=m, nn=n, dd=d: apply_combo(mm, nn, dd))

# -------------------- Animación --------------------
def update(frame):
    t = frame * DT
    
    try:
        x_screen, y_screen, z_traj, x_traj, y_traj = calculate_electron_trajectory(t, params)
        
        # Actualizar trayectorias en vistas laterales
        traj_lat.set_data(z_traj, y_traj)
        traj_top.set_data(z_traj, x_traj)
        
        # Punto actual (al final de la trayectoria - pantalla)
        pt_lat.set_data([1.0], [y_screen])
        pt_top.set_data([1.0], [x_screen])
        
        # Intensidad basada en voltaje acelerador
        intensity = beam_intensity(params["V_acc"])
        pt_lat.set_alpha(intensity)
        pt_top.set_alpha(intensity)
        
        # Traza en pantalla
        hist_x.append(x_screen)
        hist_y.append(y_screen)
        
        # Limitar historial según persistencia
        maxlen = max(1, int(params["persist_s"] * FPS))
        if len(hist_x) > maxlen:
            hist_x[:] = hist_x[-maxlen:]
            hist_y[:] = hist_y[-maxlen:]
        
        trail_scr.set_data(hist_x, hist_y)
        trail_scr.set_alpha(intensity)
        
    except Exception as e:
        # En caso de error, mantener valores anteriores
        pass
    
    return traj_lat, traj_top, pt_lat, pt_top, trail_scr

ani = FuncAnimation(fig, update, interval=1000.0/FPS, blit=True)

fig.suptitle("Simulador CRT con Física Realista - Deflexión Electromagnética", fontsize=11, y=0.97)
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.show()