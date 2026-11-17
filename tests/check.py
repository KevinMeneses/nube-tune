"""Compara los renders de tests/out con lo que dice la teoría. Sale con código 1 si algo falla."""
import sys, re, numpy as np
from measure import *

fails = 0
def scalar(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got:+10.2f}   (esperado {want:+.2f} ± {tol})")
def inrange(name, got, lo, hi):
    global fails
    ok = lo <= got <= hi; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got:+10.2f}   (entre {lo:+.2f} y {hi:+.2f})")
def text(name, got, want):
    global fails
    ok = got == want; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got!r}   (esperado {want!r})")
def rmsdb(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-20)
def tone_amp(x, sr, f, t0, t1):
    seg = x[int(t0 * sr):int(t1 * sr)]; tt = np.arange(int(t0 * sr), int(t1 * sr)) / sr
    M = np.stack([np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt)], 1)
    c, *_ = np.linalg.lstsq(M, seg, rcond=None); return 20 * np.log10(np.hypot(*c) + 1e-20)
def steady(name, want, t0=0.8, t1=3.0, sig=False):
    x, sr = load(name, sig); return cents(peak_freq(x, sr, t0, t1, want), want)
def track_cents(name, ref, fmin=60):
    """pista de tono de la salida en cents respecto a ref"""
    x, sr = load(name); T, F, A = yin(x, sr, fmin); return T, cents(F, ref)

# ---- diagnóstico del motor y sanidad de todos los renders
log = (D / "log.txt").read_text()
for name, dg in re.findall(r"^caso (\S+) .*diag=(\d+)", log, re.M):
    if int(dg): fails += 1; print("MAL", name, "el motor pidió audio que aún no llegaba (diag", dg, ")")
for p in sorted(D.glob("*.wav")):
    x, _ = load(p.stem)
    if not np.all(np.isfinite(x)) or np.abs(x).max() > 2: fails += 1; print("MAL", p.stem, "tiene NaN o pasa de +6 dBFS")
print("    diagnóstico del motor: 0 en todos los casos" if not re.search(r"diag=[1-9]", log) else "")

# ---- afinación exacta (corrección instantánea, cromática)
scalar("seno 430 Hz -> La4 440 (cents)", steady("sine430", 440), 0, 0.5)
scalar("vocal 430 Hz -> La4 440 (cents)", steady("v430", 440), 0, 0.5)
scalar("vocal 213 Hz -> Sol#3 207.65 (cents)", steady("v213", midi2f(56)), 0, 0.5)
scalar("44.1 kHz: 430 -> 440 (cents)", steady("sr44", 440), 0, 0.5)
scalar("96 kHz: 430 -> 440 (cents)", steady("sr96", 440), 0, 0.5)
scalar("La de referencia 432: 430 -> 432 (cents)", steady("v430_a432", 432), 0, 0.5)
scalar("voz grave 84 Hz (rango bajo) -> Mi2 82.41", steady("v84_bajo", midi2f(40), 1.0, 3.0), 0, 1.0)
scalar("84 Hz fuera del rango soprano: no se toca", steady("v84_soprano", 84, 1.0, 3.0), 0, 1.0)

# ---- escalas
scalar("La menor: 213 Hz -> La3 220 (no hay Sol#)", steady("v213_amin", 220), 0, 0.5)
scalar("Mi mayor: 213 Hz -> Sol#3 (si hay Sol#)", steady("v213_emaj", midi2f(56)), 0, 0.5)
scalar("personalizada (solo Sol y Do): -> Sol3 196", steady("v213_custom", midi2f(55)), 0, 0.5)

# ---- transponer (sobre la nota ya afinada)
scalar("transponer +12 -> 880 Hz (cents)", steady("v430_tr12", 880), 0, 0.5)
scalar("transponer -12 -> 220 Hz (cents)", steady("v430_trm12", 220), 0, 0.5)
scalar("transponer +7 -> Mi5 659.26 (cents)", steady("v430_tr7", midi2f(76)), 0, 0.5)
scalar("transponer -7 desde 110 -> Re2 73.42 (cents)", steady("v110_trm7", midi2f(38), 1.0, 3.0), 0, 1.0)

# ---- nivel
x0, sr = load("vowel213", True); ref = rmsdb(x0[sr:3 * sr])
for n, tol in (("v213_amin", 0.5), ("v430_tr12", 2.0), ("v430_trm12", 2.0), ("v110_tr4", 1.5)):
    x, sr = load(n); scalar(f"nivel {n} (dB respecto a la entrada)", rmsdb(x[sr:3 * sr]) - ref, 0, tol)
x, sr = load("out6"); y, _ = load("intune"); scalar("salida +6 dB", rmsdb(x[sr:3 * sr]) - rmsdb(y[sr:3 * sr]), 6, 0.1)

# ---- formantes (LPC): con 'preservar' F1/F2 no se mueven; 'siguen el tono' se mueven con el tono
x, sr = load("v110"); F0 = formants(x, sr, 1.0, 3.0)
print(f"    formantes de la entrada: F1 {F0[0]:.0f} Hz, F2 {F0[1]:.0f} Hz (síntesis: 700 / 1220)")
inrange("LPC mide bien F1 de la entrada (Hz)", F0[0], 640, 760)
for n, ratio, tol in (("v110_tr4", 1.0, 0.08), ("v110_trm7", 1.0, 0.10), ("v110_tr4_follow", 2 ** (4 / 12), 0.08),
                      ("v110_fp3", 2 ** (3 / 12), 0.08), ("v110_fm3", 2 ** (-3 / 12), 0.08)):
    x, sr = load(n); F = formants(x, sr, 1.0, 3.0) / F0
    scalar(f"{n}: F1 / F1 entrada", F[0], ratio, ratio * tol)
    scalar(f"{n}: F2 / F2 entrada", F[1], ratio, ratio * tol)
scalar("formantes +3 st: el tono no cambia (cents)", steady("v110_fp3", 110, 1.0, 3.0), 0, 1.0)

# ---- calidad: la salida sigue siendo periódica (sin aspereza agregada)
for n, fmin in (("v213_amin", 60), ("v430_tr12", 200), ("v110_tr4", 60), ("v110_trm7", 50)):
    x, sr = load(n); _, _, A = yin(x[sr:3 * sr], sr, fmin)
    inrange(f"aperiodicidad de {n} (YIN d' mediana)", np.median(A), 0, 0.05)

# ---- velocidad de corrección (arranque a 225 Hz = La3 +39 cents)
def onset_dev(name, dt):
    T, C = track_cents(name, 220); on = T[np.argmax(np.isfinite(C))]
    return np.nanmedian(C[(T >= on + dt - 0.012) & (T <= on + dt + 0.012)]), on
d, on = onset_dev("onset_s0", 0.03); print(f"    arranque de la nota en {on:.3f} s")
inrange("velocidad 0: afinado a los 30 ms (cents)", d, -2, 2)
d, _ = onset_dev("onset_s100", 0.1)
inrange("velocidad 100 ms: a los 100 ms falta ~37 % (cents)", d, 8, 22)
d, _ = onset_dev("onset_s100", 0.8)
inrange("velocidad 100 ms: a los 800 ms afinado (cents)", d, -2, 2)
T, C = track_cents("onset_s0", 220); m = (T > 0.9) & (T < 2.8)
inrange("velocidad 0: nota sostenida (cents, p95 abs)", np.nanpercentile(np.abs(C[m]), 95), 0, 2)

# ---- flex
T, C = track_cents("flex100", 220); scalar("flex 100 %: 39 ct desafinado queda en ~30 ct", np.nanmedian(C[(T > 1) & (T < 2.8)]), 39 * 0.78, 3)
T, C = track_cents("flex50", 220); scalar("flex 50 %: queda en ~22 ct", np.nanmedian(C[(T > 1) & (T < 2.8)]), 39 * 0.56, 3)

# ---- vibrato de la voz (±40 ct a 5.5 Hz, centrada 10 ct arriba)
def depth(name, t0, t1):
    T, C = track_cents(name, 220); m = (T > t0) & (T < t1) & np.isfinite(C)
    return (np.percentile(C[m], 95) - np.percentile(C[m], 5)) / 2, np.median(C[m])
dv, _ = depth("vib_s0", 0.8, 4.0); inrange("velocidad 0 aplana el vibrato (ct)", dv, 0, 5)
dv, cv = depth("vib_s200", 0.8, 4.0)
inrange("velocidad 200 ms deja el vibrato (ct)", dv, 28, 45)
inrange("velocidad 200 ms: centro afinado (ct)", cv, -4, 4)
dv, _ = depth("vib_human", 1.5, 4.0); inrange("humanizar 100 %: nota larga con vibrato (ct)", dv, 20, 45)

# ---- vibrato agregado (50 ct, 6 Hz)
T, C = track_cents("vib_add", 440); m = (T > 1) & (T < 3) & np.isfinite(C)
c = C[m] - C[m].mean(); spec = np.abs(np.fft.rfft(c * np.hanning(len(c)), 8192)); fr = np.fft.rfftfreq(8192, T[1] - T[0])
scalar("vibrato agregado: velocidad (Hz)", fr[np.argmax(spec)], 6, 0.3)
inrange("vibrato agregado: profundidad (ct)", (np.percentile(c, 97) - np.percentile(c, 3)) / 2, 42, 55)
T, C = track_cents("vib_add_delay", 440)
inrange("vibrato con retardo 1 s: quieto al principio (ct)", np.nanmax(np.abs(C[(T > 0.35) & (T < 1.1)])), 0, 6)
inrange("vibrato con retardo 1 s: vibra después (ct)", np.nanmax(np.abs(C[(T > 1.6) & (T < 3)])), 42, 58)

# ---- MIDI
scalar("MIDI nota exacta: Mi4 tocado -> 329.63", steady("midi_exact", midi2f(64)), 0, 0.5)
scalar("MIDI notas = escala (Do y La): -> La3", steady("midi_scale", 220), 0, 0.5)
scalar("MIDI secuencia: primera nota Do4", steady("midi_exact_seq", midi2f(60), 0.5, 1.4), 0, 1.0)
scalar("MIDI secuencia: segunda nota Sol4", steady("midi_exact_seq", midi2f(67), 1.7, 3.1), 0, 1.0)

# ---- transparencia y latencia
x, sr = load("mix0"); y, _ = load("vowel213", True); n = min(len(x), len(y))
inrange("mezcla 0 %: idéntica a la entrada y alineada (dB)", rmsdb(x[:n] - y[:n]) - rmsdb(y[:n]), -300, -100)
x, sr = load("intune"); y, _ = load("vowel440", True)
scalar("voz ya afinada: el tono no cambia (cents)", steady("intune", 440), 0, 0.3)
hd = [tone_amp(x, sr, 440 * h, 1, 3) - tone_amp(y, sr, 440 * h, 1, 3) for h in range(1, 13)]
inrange("voz ya afinada: armónicos 1-12 sin cambio (dB, máx)", max(np.abs(hd)), 0, 0.5)
x, sr = load("noise"); y, _ = load("noise", True); n = min(len(x), len(y))
inrange("ruido (sin tono) pasa intacto (dB del residuo)", rmsdb(x[:n] - y[:n]) - rmsdb(y[:n]), -300, -60)
x, _ = load("silence"); inrange("silencio sigue en silencio (dBFS)", 20 * np.log10(np.abs(x).max() + 1e-30), -1000, -150)
x, sr = load("mix50")
inrange("mezcla 50 %: original 213 Hz presente (dB)", tone_amp(x, sr, 213, 1, 3) - tone_amp(x, sr, 220, 1, 3), -3, 3)

# ---- glissando con corrección dura: escalera limpia y sin huecos
T, C = track_cents("glide", 440); C = C[(T > 0.5) & (T < 3.0)]; C = C[np.isfinite(C)]
r = np.abs(((C + 50) % 100) - 50)
inrange("glissando: cuadros pegados a un semitono (%)", 100 * np.mean(r < 5), 85, 100)
x, sr = load("glide"); fr = np.sqrt(np.mean(x[int(0.5 * sr):int(3 * sr)].reshape(-1, sr // 50) ** 2, 1))
inrange("glissando: sin huecos (cuadro mínimo vs mediana, dB)", 20 * np.log10(fr.min() / np.median(fr)), -6, 0)

# ---- aprender tonalidad
m = re.search(r"^caso learn_em .*tonalidad=(\S+) \| escala=(\S+)", log, re.M)
text("aprender tonalidad: melodía en Mi menor", (m.group(1), m.group(2)) if m else None, ("E", "Menor"))

# ---- notas dibujadas (línea de tiempo del proyecto)
def notes(name):
    x, sr = load(name); T, F, A = yin(x, sr, 60); return T, 69 + 12 * np.log2(F / 440)
def nmed(T, N, t0, t1): return np.nanmedian(N[(T > t0) & (T < t1)])
T, N = notes("seg_line")
scalar("nota dibujada Do4 en 1-2 s (cents)", 100 * (nmed(T, N, 1.15, 1.9) - 60), 0, 0.5)
scalar("antes de la nota: escala (Sol#3, cents)", 100 * (nmed(T, N, 0.3, 0.9) - 56), 0, 0.5)
scalar("después de la nota: escala (Sol#3, cents)", 100 * (nmed(T, N, 2.15, 3.0) - 56), 0, 0.5)
m = (T > 0.9) & (T < 1.2); on = T[m][np.argmax(N[m] > 58)]
m = (T > 1.9) & (T < 2.2); off = T[m][np.argmax(N[m] < 58)]
inrange("la nota empieza a tiempo (s; YIN marca ~6 ms tarde)", on, 1.0, 1.03)
inrange("la nota termina a tiempo (s)", off, 2.0, 2.03)
T, N = notes("seg_glide"); m = (T > 1.15) & (T < 1.85) & np.isfinite(N); k = np.polyfit(T[m], N[m], 1)
scalar("deslizamiento La3 -> Mi4 en 1 s: pendiente (st/s)", k[0], 7, 0.1)
inrange("deslizamiento: atraso (ms; YIN marca ~6 ms tarde)", 1000 * (60.5 - np.polyval(k, 1.5)) / 7, 0, 15)
T, N = notes("seg_nat")
scalar("fuera de las notas = natural: 213 Hz sin tocar (ct)", 100 * (nmed(T, N, 0.3, 0.9) - (69 + 12 * np.log2(213 / 440))), 0, 1)
scalar("  y dentro de la nota: La3 (cents)", 100 * (nmed(T, N, 1.15, 1.9) - 57), 0, 0.5)
T, N = notes("seg_ignore"); scalar("notas ignoradas (A/B): sigue en la escala (ct)", 100 * (nmed(T, N, 1.15, 1.9) - 56), 0, 0.5)
T, N = notes("seg_tr12")
scalar("transponer +12: la nota dibujada manda (Do4, ct)", 100 * (nmed(T, N, 1.15, 1.9) - 60), 0, 0.5)
scalar("  y fuera sube la octava (Sol#4, ct)", 100 * (nmed(T, N, 0.3, 0.9) - 68), 0, 0.5)
T, N = notes("seg_cents")
scalar("nota con cents (59.5) recortada por otra (ct)", 100 * (nmed(T, N, 1.1, 1.45) - 59.5), 0, 0.5)
scalar("  la que la pisa (Do#4, ct)", 100 * (nmed(T, N, 1.6, 2.45) - 61), 0, 0.5)
T, N = notes("seg_detect")
text("detectar notas: una nota en la vocal sostenida", re.search(r"^caso seg_detect .*notas=(\S+)", log, re.M).group(1), "1.0")
scalar("detectar notas (fuera = natural): queda en Sol#3 (ct)", 100 * (nmed(T, N, 0.3, 3.0) - 56), 0, 0.5)
T, N = notes("seg_reload"); scalar("las notas se guardan con el proyecto (Mi3, ct)", 100 * (nmed(T, N, 1.15, 1.9) - 52), 0, 0.5)

# ---- voz real (si está la grabación)
if (D / "voz_seca.wav").exists():
    xs, sr = load("voz_seca")
    Ts, Fs, As = yin(xs, sr, 70)
    def voz(name):
        x, _ = load(name); T, F, A = yin(x, sr, 70); return x, F, A
    def dev(F): c = cents(F, 440) % 100; return np.abs(np.where(c > 50, c - 100, c))
    vs = np.isfinite(Fs)
    din = np.nanmedian(dev(Fs[vs]))
    x, F, A = voz("voz_hard"); both = vs & np.isfinite(F)
    print(f"    voz real: {vs.mean() * 100:.0f} % de cuadros con tono; desafinación de la entrada (mediana) {din:.1f} ct")
    inrange("voz hard tune: desafinación mediana (ct)", np.median(dev(F[both])), 0, 3)
    inrange("voz hard tune: p90 (ct)", np.percentile(dev(F[both]), 90), 0, 12)
    clean = both & (As < 0.1) & (A < 0.1)          # cuadros limpios (sin transiciones ni consonantes)
    jump = np.abs(cents(F[clean], Fs[clean])) > 100
    inrange("voz hard tune: saltos de octava (% cuadros limpios)", 100 * jump.mean(), 0, 0.5)
    inrange("voz hard tune: corrección p99 (ct, máx teórico 50)", np.percentile(np.abs(cents(F[clean], Fs[clean])), 99), 0, 50)
    inrange("voz hard tune: aperiodicidad agregada (d')", np.median(A[both]) - np.median(As[both]), -1, 0.04)
    scalar("voz hard tune: nivel (dB)", rmsdb(x) - rmsdb(xs), 0, 1.0)
    x, F, A = voz("voz_natural"); both = vs & np.isfinite(F)
    inrange("voz natural: más afinada que la entrada (ct)", np.median(dev(F[both])), 0, din * 0.8)
    x, F, A = voz("voz_pop"); both = vs & np.isfinite(F)
    inrange("voz pop: desafinación mediana (ct)", np.median(dev(F[both])), 0, 5)
    for n, st in (("voz_tr12", 12), ("voz_trm12", -12)):
        x, F, A = voz(n); both = vs & np.isfinite(F)
        scalar(f"{n}: salto medido (semitonos)", np.median(cents(F[both], Fs[both])) / 100, st, 0.3)
        scalar(f"{n}: nivel (dB)", rmsdb(x) - rmsdb(xs), 0, 3)
    x, F, A = voz("seg_detect_voz"); both = vs & np.isfinite(F)
    nv = float(re.search(r"^caso seg_detect_voz .*notas=(\S+)", log, re.M).group(1))
    inrange("voz: detectar notas (cantidad en 30 s)", nv, 20, 200)
    inrange("voz: notas detectadas = afinada (ct)", np.median(dev(F[both])), 0, 3)
    scalar("voz: notas detectadas, nivel (dB)", rmsdb(x) - rmsdb(xs), 0, 1.0)
    for p in (4, 5, 6, 9, 10, 11, 12, 13):
        x, _ = load(f"preset{p}"); inrange(f"preset {p}: nivel razonable (dB)", rmsdb(x) - rmsdb(xs), -4, 4)
print("\nFALLAS:", fails)
sys.exit(1 if fails else 0)
