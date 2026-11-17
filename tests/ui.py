"""Ayudante para probar la interfaz con cliclick (ventana del FX con su tamaño por defecto, 1000 x 640 de área gráfica).
Las coordenadas son puntos dentro del área gráfica, calculadas como en @gfx (SC = 1). Mismo arnés que Nube Sampler."""
import subprocess, time, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
R = "/Applications/REAPER.app/Contents/MacOS/REAPER"
HDR = 52.5                      # cabecera de REAPER (título, presets) sobre el área gráfica

def win():
    s = subprocess.run(["osascript", "-e", 'tell application "System Events" to tell process "REAPER" to get {position, size} of '
                        '(first window whose name contains "JS: Nube Tune")'], capture_output=True, text=True).stdout
    x, y, w, h = [int(v) for v in s.replace(",", " ").split()]; return x, y, w, h
WX, WY = 32, 117.5
def locate():
    global WX, WY
    x, y, _, _ = win(); WX, WY = x, y + HDR
def pt(x, y): return f"{round(WX + x)},{round(WY + y)}"
def cc(*args): subprocess.run(["cliclick", "-w", "100", *args], check=True); time.sleep(0.35)
def focus(): cc(f"m:{pt(965, 22)}", "w:100", f"dd:{pt(965, 22)}", "w:150", f"du:{pt(965, 22)}", "w:200")     # barra superior sin controles: el primer clic tras un script solo activa la ventana
activate = focus
def click(x, y): focus(); cc(f"m:{pt(x, y)}", "w:150", f"dd:{pt(x, y)}", "w:200", f"du:{pt(x, y)}")
def dclick(x, y): focus(); cc(f"m:{pt(x, y)}", f"dd:{pt(x, y)}", f"du:{pt(x, y)}", f"dd:{pt(x, y)}", f"du:{pt(x, y)}")
def hover(x, y): focus(); cc(f"m:{pt(x, y)}")
def wheel(n): subprocess.run(["swift", str(ROOT / "tests/scroll.swift"), str(n)], check=True); time.sleep(0.4)
def shot(path):
    """captura de la ventana por su id (no la trae al frente ni le quita el foco)"""
    wid = subprocess.run(["swift", str(ROOT / "tests/winid.swift"), "JS: Nube Tune"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["screencapture", "-x", "-o", f"-l{wid}", path], check=True); return path
def lua(name): subprocess.Popen([R, "-nonewinst", str(ROOT / "tests" / name)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dump():
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True); lua("ui_dump.lua")
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): return p.read_text().replace("done\n", "")
        time.sleep(0.25)
    return "(sin respuesta)"
def param(n):
    """valor formateado del slider n"""
    m = re.search(rf"^{n} (.*)$", dump(), re.M); return m.group(1).rsplit(" = ", 1)[1] if m else None
def num(s):
    try: return float(s.split()[0])
    except Exception: return float("nan")
def drag(x0, y0, x1, y1, steps=8):
    focus(); cc(f"m:{pt(x0, y0)}", "w:150", f"dd:{pt(x0, y0)}", "w:250")
    for k in range(1, steps + 1): cc(f"m:{pt(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)}")
    cc(f"du:{pt(x1, y1)}")

def rclick(x, y): focus(); cc(f"m:{pt(x, y)}", "w:150", f"rc:{pt(x, y)}")
# ---- layout (área gráfica de 1000 x 640 pt): barra de modo en y 50-74, dy = 82, dh = 344, py = 436
PY = 436
PRESETS, TONO, ESCALA, VOZ, MIDI = (208, 22), (322, 22), (476, 22), (673, 22), (850, 22)
GRAPH = (396, 240); STRIP_X = 30
# barra de modo y editor de notas (en el editor la gráfica va de x 54 a 986; regla de compases y 82-100)
TB_Y = 62
TAB_VIVO, TAB_EDITAR = (57, TB_Y), (162, TB_Y)
DETECTAR, DESHACER, BORRAR, FUERA, COMPARAR = (291, TB_Y), (396, TB_Y), (494, TB_Y), (642, TB_Y), (805, TB_Y)
REGLA_Y = 91
KB_Y0 = PY + 28
WHITE = lambda i: (14 + 42 * i + 21, KB_Y0 + 72)          # 0 = C, 1 = D ... 6 = B
BLACK = lambda pos: (14 + 42 * pos, KB_Y0 + 26)           # pos 1 = C#, 2 = D#, 4 = F#, 5 = G#, 6 = A#
FORMANTES_BTN, APRENDER = (87, PY + 137), (230, PY + 137)
KY = PY + 98
VELOCIDAD = (366, KY)
KNOB = {"humanizar": (466, KY), "flex": (550, KY), "formantes": (640, KY), "transponer": (724, KY),
        "mezcla": (814, KY), "salida": (898, KY)}
SMALL = {"vib_prof": (792, 298), "vib_vel": (868, 298), "vib_ret": (944, 298),
         "sens": (792, 390), "puerta": (868, 390), "la": (944, 390)}
