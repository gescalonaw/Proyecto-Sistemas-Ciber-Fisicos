"""Plan de pruebas del simulador (casos P1-P6). Ejecuta cada caso y reporta PASA/FALLA."""
import os
from datetime import datetime
import numpy as np
from cps_lazo import Params, Ataque, simular, respuesta_analitica

p = Params(T_end=600.0)
k0 = 3000                      # ataque desde t = 300 s (lazo ya en regimen)
resultados = []

def reg(caso, descr, valor, criterio, ok):
    resultados.append((caso, descr, valor, criterio, ok))

# P1: sin ataque vs respuesta analitica (OE1)
r0 = simular(p, Ataque("ninguno"))
rms = np.sqrt(np.mean((r0["T"][:2000] - respuesta_analitica(r0["t"][:2000], p)) ** 2))
reg("P1", "Sin ataque vs analitica (primeros 200 s)", f"RMS = {rms:.4f} °C ({rms/p.r*100:.2f} % de r)", "<= 5 % de r", rms / p.r * 100 <= 5)

# P2: canal identidad con a=0, d=0
reg("P2", "Canal sin ataque: ya = y", f"max|ya-y| = {np.max(np.abs(r0['ya']-r0['y'])):.1e}", "= 0", np.allclose(r0["ya"], r0["y"]))

# P3: bias
b = 2.0
r3 = simular(p, Ataque("bias", k0, b))
Tf = r3["T"][-500:].mean()
reg("P3", f"Bias b = {b:g} °C: T real final", f"T = {Tf:.2f} °C (r - b = {p.r-b:.2f})", "|T-(r-b)| <= 0,1 °C", abs(Tf - (p.r - b)) <= 0.1)

# P4: rampa
rho = 0.05
r4 = simular(p, Ataque("rampa", k0, rho))
kk = k0 + 1000                  # 100 s despues del inicio (antes de tocar el piso T_amb)
dT = p.r - r4["T"][kk]
reg("P4", f"Rampa rho = {rho:g} °C/s: desvio real a los 100 s", f"r - T = {dT:.2f} °C; d = {r4['d'][kk]:.2f} °C", "T se aleja de r (> 5 sigma_y)", dT > 5 * p.sigma_y)

# P5: DoS con hold y con ya=0
L = 30
r5 = simular(p, Ataque("dos", k0, L))
r5z = simular(p, Ataque("dos", k0, L), hold_on_loss=False)
dev = np.max(np.abs(r5["T"][k0:k0 + 600] - p.r))
reg("P5a", f"DoS L = {L} muestras (3 s), controlador mantiene ultimo valor", f"max|T-r| = {dev:.3f} °C; muestras con a=1: {int(r5['a'].sum())}", "a=1 exactamente L veces", int(r5["a"].sum()) == L)
reg("P5b", "DoS con ya = 0 (sin mantener): u en la rafaga", f"u max = {r5z['u'][k0:k0+L].max():.0f} W (P_max = {p.P_max:g})", "satura (= P_max)", r5z["u"][k0:k0 + L].max() >= p.P_max - 1e-9)

# P6: replay en regimen: estadisticas conservadas
tau_r = 10.0
r6 = simular(p, Ataque("replay", k0, tau_r))
ya, y = r6["ya"][k0:], r6["y"][k0:]
dm, ds = ya.mean() - y.mean(), ya.std() - y.std()
reg("P6", f"Replay tau_r = {tau_r:g} s en regimen: media y desv. de ya vs y", f"dif. media = {dm:+.4f} °C; dif. desv. = {ds:+.4f} °C", "|dif| < 0,02 °C (indistinguible)", abs(dm) < 0.02 and abs(ds) < 0.02)

lineas = [f"{c:4s} | {d} | {v} | criterio: {cr} | {'PASA' if ok else 'FALLA'}" for c, d, v, cr, ok in resultados]
lineas.insert(0, f"Fecha de ejecucion: {datetime.now():%Y-%m-%d %H:%M:%S} | semilla = {p.seed}")
os.makedirs("resultados", exist_ok=True)
with open("resultados/pruebas_basicas.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lineas) + "\n")
print("\n".join(lineas))
