# Proyecto-Sistemas-Ciber-Fisicos
Análisis y Diseño de Sistemas Ciber-Físicos, UdeC 2026-2.
Integrantes: Pablo Bettancourt P., Gabriela Escalona W., Diego San Martín A., Bastián Zapata P.

## Contenido
- `cps_lazo.py`: planta (cámara térmica de 1.er orden, ZOH), controlador PI, canal
  `ya(k) = [1 - a(k)] y(k) + d(k)` y ataques parametrizables (bias, rampa, DoS, replay).
- `hito1_lazo_sin_ataque.py`: primer hito. Lazo cerrado sin ataque vs. respuesta analítica.
- `resultados/`: figura, log CSV y resumen con fecha del primer hito.

## Ejecución
```
pip install -r requirements.txt
python hito1_lazo_sin_ataque.py
```

## Parámetros (Tabla 4 del informe)
tau = 50 s, K = 0,5 °C/W, T_amb = 20 °C, P_max = 100 W, sigma_y = 0,1 °C, Ts = 0,1 s.
PI con Ti = tau y Kp*K = 5 (tau_c = 10 s). Consigna r = 28 °C.

## Convenciones
- DoS de duración L: a(k) = 1 para k0 <= k < k0 + L. Con `hold_on_loss=True` el controlador
  mantiene la última medición válida; con False usa ya = 0.
- Replay: ya(k) = y(k - tau_r/Ts).

## Pendiente
Filtro de Kalman + CUSUM, calibración de ARL0 y curvas Monte Carlo (Entregas 2 y 3).