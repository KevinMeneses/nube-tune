"""Ayudante para probar la interfaz con cliclick (ventana del FX en su posición/tamaño por defecto)."""
import subprocess, time, pathlib, re
WX, WY = 32, 117.5           # esquina del área gráfica del FX (puntos), medida en una captura
ROOT = pathlib.Path(__file__).resolve().parent.parent
def pt(x, y): return f"{round(WX + x)},{round(WY + y)}"
def cc(*args): subprocess.run(["cliclick", "-w", "60", *args], check=True); time.sleep(0.4)
def click(x, y):
    """clic lento (bajar, esperar, subir): JSFX lee el mouse una vez por cuadro y un clic instantáneo se puede perder"""
    activate(); cc(f"m:{pt(x, y)}"); cc(f"dd:{pt(x, y)}"); cc(f"du:{pt(x, y)}")
def activate():
    """clic en el pie (sin controles): cada ui_dump.lua deja la ventana del FX inactiva y el primer clic solo la activa"""
    cc(f"c:{pt(300, 630)}")
def wheel(n): subprocess.run(["swift", str(ROOT / "tests/scroll.swift"), str(n)], check=True); time.sleep(0.4)
def shot(path): subprocess.run(["screencapture", "-x", "-R32,117,1000,640", path], check=True); time.sleep(0.5); activate(); return path
def dump():
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True)
    subprocess.Popen(["/Applications/REAPER.app/Contents/MacOS/REAPER", "-nonewinst", str(ROOT / "tests/ui_dump.lua")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): return p.read_text().replace("done\n", "")
        time.sleep(0.25)
    return "(sin respuesta)"
def param(n):
    """valor formateado del slider n"""
    m = re.search(rf"^{n} (.*)$", dump(), re.M); return m.group(1).rsplit(" = ", 1)[1] if m else None
def num(s): return float(s.split()[0]) if s else float("nan")
def drag(x0, y0, x1, y1, steps=8):
    activate(); cc(f"m:{pt(x0, y0)}"); cc(f"dd:{pt(x0, y0)}")
    for k in range(1, steps + 1): cc(f"m:{pt(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)}")
    cc(f"du:{pt(x1, y1)}")
# layout (ventana 1000x640): dy = 54, dh = 372, py = 436
PY = 436
PRESETS, TONO, ESCALA, VOZ, MIDI = (208, 22), (322, 22), (476, 22), (673, 22), (850, 22)
GRAPH = (396, 240); STRIP_X = 30
KB_Y0 = PY + 28
WHITE = lambda i: (14 + 42 * i + 21, KB_Y0 + 72)          # 0 = C, 1 = D ... 6 = B
BLACK = lambda pos: (14 + 42 * pos, KB_Y0 + 26)           # pos 1 = C#, 2 = D#, 4 = F#, 5 = G#, 6 = A#
FORMANTES_BTN, APRENDER = (87, PY + 137), (230, PY + 137)
KY = PY + 98
VELOCIDAD = (366, KY)
KNOB = {"humanizar": (466, KY), "flex": (550, KY), "formantes": (640, KY), "transponer": (724, KY),
        "mezcla": (814, KY), "salida": (898, KY)}
SMALL = {"vib_prof": (792, 270), "vib_vel": (868, 270), "vib_ret": (944, 270),
         "sens": (792, 362), "puerta": (868, 362), "la": (944, 362)}
