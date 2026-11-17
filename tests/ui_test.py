"""Pruebas de la interfaz con el mouse. Requiere la demo abierta (NUBE_KEY=9 NUBE_SCALE=2 tests/reopen.sh: preset 2,
La menor) y la ventana del FX al frente. OJO: mueve el mouse de verdad; no correr mientras alguien usa REAPER.
JSFX lee el mouse a 60 Hz y cada ui_dump.lua le quita el foco a la ventana (igual que en Nube Sampler):
si una acción no cambió nada se repite UNA vez y se cuenta en 'reintentos'. Un control que no responde falla igual."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ui import *
OUT = os.environ.get("NUBE_SHOTS", str(ROOT / "tests/out"))
fails = 0; retries = 0
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:48s} {got!r}")
def act(action, probe):
    """hace la acción; si 'probe' (lectura del estado) no cambió, la repite una vez"""
    global retries
    before = probe(); action(); after = probe()
    if after == before: retries += 1; action(); after = probe()
    return after
def mask(): return int(num(param(14)))
def menu(pos, downs):
    click(*pos); time.sleep(0.6); cc(*(["kp:arrow-down"] * downs), "kp:return")
AMIN = 1 << 9 | 1 << 11 | 1 << 0 | 1 << 2 | 1 << 4 | 1 << 5 | 1 << 7
DMIN = 1 << 2 | 1 << 4 | 1 << 5 | 1 << 7 | 1 << 9 | 1 << 10 | 1 << 0

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
locate(); focus(); time.sleep(0.5); focus(); time.sleep(0.5)   # calentamiento: el primer clic solo activa la ventana
check("arranca con preset 2 (velocidad 20 ms)", num(param(1)), 20.0)
check("arranca en La menor", (param(12), param(13)), ("A", "Menor"))
x, y = VELOCIDAD
check("arrastrar Velocidad hacia arriba sube", num(act(lambda: drag(x, y, x, y - 50), lambda: param(1))), lambda v: v > 40)
check("doble clic en Velocidad = 20 ms", num(act(lambda: dclick(x, y), lambda: param(1))), 20.0)
x, y = KNOB["humanizar"]
check("rueda sobre Humanizar sube", num(act(lambda: (hover(x, y), wheel(5)), lambda: param(2))), lambda v: v > 22)
x, y = KNOB["transponer"]
check("arrastrar Transponer: semitonos enteros > 0", num(act(lambda: drag(x, y, x, y - 40), lambda: param(5))), lambda v: v > 0 and v == int(v))
check("doble clic en Transponer = 0", num(act(lambda: dclick(x, y), lambda: param(5))), 0.0)
act(lambda: click(*BLACK(1)), lambda: param(13))
check("clic en C# (no esta en La menor): escala personalizada", param(13), "Personalizada")
check("  C# activa y las demas de La menor intactas", mask(), AMIN | 2)
check("otro clic en C#: se quita", (act(lambda: click(*BLACK(1)), mask) >> 1) & 1, 0)
check("clic en C (tecla blanca): se quita", act(lambda: click(*WHITE(0)), mask) & 1, 0)
check("boton Preservar formantes -> siguen el tono", act(lambda: click(*FORMANTES_BTN), lambda: param(18)), "Siguen el tono")
check("otro clic -> Preservar", act(lambda: click(*FORMANTES_BTN), lambda: param(18)), "Preservar")
check("menu Tono -> D", act(lambda: menu(TONO, 3), lambda: param(12)), "D")
check("menu Escala -> Menor", act(lambda: menu(ESCALA, 3), lambda: param(13)), "Menor")
check("menu Voz -> Baritono / Bajo", act(lambda: menu(VOZ, 3), lambda: param(15)), lambda v: v.startswith("Baritono"))
x, y = SMALL["vib_prof"]
check("arrastrar Vibrato profundidad sube", num(act(lambda: drag(x, y, x, y - 40), lambda: param(7))), lambda v: v > 5)
x, y = KNOB["mezcla"]
check("rueda abajo en Mezcla baja", num(act(lambda: (hover(x, y), wheel(-5)), lambda: param(10))), lambda v: v < 100)
x, y = SMALL["la"]
act(lambda: drag(x, y, x, y - 30), lambda: param(6))
check("doble clic en La (A4) = 440", num(act(lambda: dclick(x, y), lambda: param(6))), 440.0)
act(lambda: click(STRIP_X, GRAPH[1]), mask)
check("clic en un nombre de nota de la grafica la alterna", (param(13), bin(mask() ^ DMIN).count("1")), ("Personalizada", 1))
check("Aprender tono -> escuchando", act(lambda: click(*APRENDER), lambda: param(20)), "Escuchando")
time.sleep(4); shot(f"{OUT}/ui_aprendiendo.png")
check("Aprender otra vez -> apagado", act(lambda: click(*APRENDER), lambda: param(20)), "No")
check("  y deja una escala mayor o menor", param(13), lambda v: v in ("Mayor", "Menor"))
check("menu Presets -> Hard tune (velocidad 0)", num(act(lambda: menu(PRESETS, 3), lambda: param(1))), 0.0)
shot(f"{OUT}/ui_hard.png")
print(f"reintentos (eventos perdidos por el arnes): {retries}")
print("FALLAS:", fails)
sys.exit(1 if fails else 0)
