"""Lazo cerrado de temperatura en red con canal atacable (proyecto S2).

Planta: camara termica de primer orden, discretizada exacta (ZOH).
Canal:  ya(k) = [1 - a(k)] y(k) + d(k); replay: ya(k) = y(k - tau_r/Ts).
"""
from dataclasses import dataclass
import numpy as np


@dataclass
class Params:
    tau: float = 50.0       # constante de tiempo [s]
    K: float = 0.5          # ganancia estatica [°C/W]
    T_amb: float = 20.0     # temperatura ambiente [°C]
    P_max: float = 100.0    # potencia maxima [W]
    sigma_y: float = 0.1    # desviacion del ruido de medicion [°C]
    Ts: float = 0.1         # periodo de muestreo [s]
    Kp: float = 10.0        # ganancia proporcional [W/°C]  (Kp*K = 5)
    Ti: float = 50.0        # tiempo integral [s]           (Ti = tau)
    r: float = 28.0         # consigna [°C]
    T_end: float = 200.0    # duracion de la simulacion [s]
    seed: int = 1


@dataclass
class Ataque:
    """tipo: ninguno | bias | rampa | dos | replay.
    magnitud: bias [°C], pendiente rho [°C/s], duracion L [muestras], retardo tau_r [s]."""
    tipo: str = "ninguno"
    k0: int = 0
    magnitud: float = 0.0


def canal(k, y, atq, Ts):
    """Devuelve (ya_k, a_k, d_k) para la muestra k."""
    a, d = 0, 0.0
    if atq.tipo == "bias" and k >= atq.k0:
        d = atq.magnitud
    elif atq.tipo == "rampa" and k >= atq.k0:
        d = atq.magnitud * Ts * (k - atq.k0)
    elif atq.tipo == "dos" and atq.k0 <= k < atq.k0 + int(atq.magnitud):
        a = 1
    ya = (1 - a) * y[k] + d
    if atq.tipo == "replay" and k >= atq.k0:
        ya = y[max(0, k - int(round(atq.magnitud / Ts)))]
    return ya, a, d


def simular(p=Params(), atq=Ataque(), hold_on_loss=True):
    """Simula el lazo cerrado. Si hold_on_loss, el controlador mantiene la
    ultima medicion valida cuando a(k)=1; si no, usa ya=0 (segun la ecuacion)."""
    rng = np.random.default_rng(p.seed)
    N = int(round(p.T_end / p.Ts))
    ad = np.exp(-p.Ts / p.tau)
    bd = p.K * (1 - ad)
    T = np.empty(N + 1); T[0] = p.T_amb
    y, ya, u = np.empty(N), np.empty(N), np.empty(N)
    am, dv = np.zeros(N, dtype=int), np.zeros(N)
    I, ya_last = 0.0, p.T_amb
    for k in range(N):
        y[k] = T[k] + p.sigma_y * rng.standard_normal()
        ya[k], am[k], dv[k] = canal(k, y, atq, p.Ts)
        yc = ya_last if (am[k] and hold_on_loss) else ya[k]
        if not am[k]:
            ya_last = ya[k]
        e = p.r - yc
        u_raw = p.Kp * e + I
        u[k] = min(max(u_raw, 0.0), p.P_max)
        if u_raw == u[k]:                       # anti-windup: integra sin saturar
            I += p.Kp / p.Ti * p.Ts * e
        T[k + 1] = p.T_amb + ad * (T[k] - p.T_amb) + bd * u[k]
    t = np.arange(N) * p.Ts
    return dict(t=t, T=T[:-1], y=y, ya=ya, u=u, a=am, d=dv)


def respuesta_analitica(t, p=Params()):
    """Lazo cerrado con PI (Ti = tau): primer orden con tau_c = tau/(Kp*K)."""
    tau_c = p.tau / (p.Kp * p.K)
    return p.T_amb + (p.r - p.T_amb) * (1 - np.exp(-t / tau_c))
