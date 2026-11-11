"""Primer hito S2: lazo cerrado sin ataque, con el canal ya(k) implementado,
contrastado con la respuesta analitica. Genera figura, log CSV y resumen."""
import os
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cps_lazo import Params, Ataque, simular, respuesta_analitica

p = Params()
res = simular(p, Ataque("ninguno"))
Tan = respuesta_analitica(res["t"], p)

rms = np.sqrt(np.mean((res["T"] - Tan) ** 2))
rel = rms / p.r * 100
# canal sin ataque: ya debe ser igual a y
assert np.allclose(res["ya"], res["y"]), "con a=0 y d=0, ya debe ser igual a y"

os.makedirs("resultados", exist_ok=True)
ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

fig, ax = plt.subplots(2, 1, figsize=(7.5, 5.2), sharex=True,
                       gridspec_kw={"height_ratios": [3, 1.4]})
ax[0].plot(res["t"], res["ya"], color="#bbb", lw=0.7, label=r"medición $y_a(k)$")
ax[0].plot(res["t"], res["T"], color="#1f5fa8", lw=1.6, label="temperatura real $T$ (simulada)")
ax[0].plot(res["t"], Tan, "--", color="#c0392b", lw=1.4, label="respuesta analítica")
ax[0].axhline(p.r, color="k", lw=0.6, ls=":", label=f"consigna r = {p.r:g} °C")
ax[0].set_ylabel("Temperatura [°C]"); ax[0].legend(loc="lower right", fontsize=8)
ax[0].set_title(f"Lazo cerrado sin ataque: error RMS = {rms:.3f} °C ({rel:.2f} % del valor final)", fontsize=10)
ax[1].plot(res["t"], res["u"], color="#2f6b2f", lw=1.0)
ax[1].set_ylabel("u [W]"); ax[1].set_xlabel("Tiempo [s]")
for a_ in ax: a_.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("resultados/hito1_lazo_sin_ataque.png", dpi=200)

np.savetxt("resultados/hito1_log.csv",
           np.column_stack([res["t"], res["T"], res["y"], res["ya"], res["u"], res["a"], res["d"]]),
           delimiter=",", header="t_s,T_real_C,y_C,ya_C,u_W,a,d", comments="", fmt="%.6f")
with open("resultados/hito1_resumen.txt", "w", encoding="utf-8") as f:
    f.write(f"Fecha de ejecucion: {ahora}\nSemilla: {p.seed}\n"
            f"Error RMS vs analitica: {rms:.4f} °C ({rel:.2f} % de r)\n"
            f"Meta OE1: <= 5 % -> {'CUMPLE' if rel <= 5 else 'NO CUMPLE'}\n"
            f"u_max usada: {res['u'].max():.1f} W (P_max = {p.P_max:g} W)\n")
print(open("resultados/hito1_resumen.txt", encoding="utf-8").read())
