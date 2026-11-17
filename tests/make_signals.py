"""Señales de prueba (float32). La "vocal" es aditiva: armónicos en fase coseno (pulsos glotales) con una envolvente
de formantes conocida (vocal 'a': F1 700, F2 1220, F3 2600 Hz), así se puede medir si los formantes se preservan."""
import numpy as np, soundfile as sf, pathlib, shutil
D = pathlib.Path(__file__).parent / "signals"; D.mkdir(exist_ok=True)
FORM = [(700, 80), (1220, 90), (2600, 120)]

def envelope(f):
    """magnitud de la envolvente espectral (resonadores de 2 polos + caída de -6 dB/oct)"""
    f = np.asarray(f, float); h = np.ones_like(f)
    for fc, bw in FORM:
        h *= fc * fc / np.sqrt((fc * fc - f * f) ** 2 + (bw * f) ** 2)
    return h / np.sqrt(1 + (f / 150) ** 2)

def vowel(f0, sr, rms_db=-20):
    """f0: arreglo con la frecuencia por muestra (0 = silencio)"""
    f0 = np.asarray(f0, float); n = len(f0)
    ph = 2 * np.pi * np.cumsum(f0) / sr
    on = f0 > 0
    x = np.zeros(n)
    hmax = int(sr * 0.45 / max(f0[on].min(), 20))
    for h in range(1, hmax + 1):
        fh = h * f0
        a = np.where(fh < sr * 0.45, envelope(fh), 0)
        if not a.any(): break
        x += a * np.cos(h * ph)
    # rampas de 5 ms en los bordes de cada nota
    edge = np.diff(np.r_[0, on.astype(int), 0])
    r = int(sr * 0.005); g = on.astype(float)
    for s in np.where(edge == 1)[0]: g[s:s + r] *= np.linspace(0, 1, r)[:len(g[s:s + r])]
    for e in np.where(edge == -1)[0]: g[max(e - r, 0):e] *= np.linspace(1, 0, r)[-len(g[max(e - r, 0):e]):]
    x *= g
    x *= 10 ** (rms_db / 20) / np.sqrt(np.mean(x[on] ** 2))
    return x

def save(name, x, sr=48000):
    sf.write(D / name, np.stack([x, x], 1).astype(np.float32), sr, subtype="FLOAT")

def const(f, dur, sr=48000, lead=0.25):
    return np.r_[np.zeros(int(sr * lead)), np.full(int(sr * dur), float(f))]

SR = 48000
t = np.arange(SR * 3) / SR
save("sine430.wav", np.r_[np.zeros(SR // 4), 0.25 * np.sin(2 * np.pi * 430 * t)])
for f in (430, 213, 440, 110):
    save(f"vowel{f}.wav", vowel(const(f, 3), SR))
save("vowel84.wav", vowel(const(84, 3), SR))
save("vowel430_44k.wav", vowel(const(430, 3, 44100), 44100), 44100)
save("vowel430_96k.wav", vowel(const(430, 3, 96000), 96000), 96000)
# vibrato: 220 Hz +10 cents, ±40 cents a 5.5 Hz
tv = np.arange(SR * 4) / SR
save("vib220.wav", vowel(np.r_[np.zeros(SR // 4), 220 * 2 ** ((10 + 40 * np.sin(2 * np.pi * 5.5 * tv)) / 1200)], SR))
# arranque tras silencio a 225 Hz (La3 +39 cents)
save("onset225.wav", vowel(const(225, 2.5, SR, 0.5), SR))
# glissando 200 -> 400 Hz en 3 s
tg = np.arange(SR * 3) / SR
save("glide.wav", vowel(np.r_[np.zeros(SR // 4), 200 * 2 ** (tg / 3)], SR))
# ruido blanco (-20 dBFS RMS) y silencio
rng = np.random.default_rng(1)
save("noise.wav", 0.1 * rng.standard_normal(SR * 3))
save("silence.wav", np.zeros(SR * 2))
# melodía en Mi menor (notas de 0.3 s, la tónica y la quinta pesan más)
mel = [64, 67, 71, 69, 67, 66, 64, 59, 64, 62, 64, 67, 71, 72, 71, 69, 67, 64, 66, 67, 64, 71, 64, 64]
f0 = np.concatenate([np.r_[np.full(int(SR * 0.28), 440 * 2 ** ((n - 69) / 12) * 2 ** (rng.uniform(-20, 20) / 1200)),
                           np.zeros(int(SR * 0.04))] for n in mel])
save("melody_em.wav", vowel(np.r_[np.zeros(SR // 4), f0], SR))
# voz real (grabación propia, no está en el repo): 30 s de la voz seca de Nube baja
v = pathlib.Path.home() / "Music/ClaudeBeats/Media/voz_sola_seca.wav"
if v.exists():
    x, sr = sf.read(v, start=20 * 48000, stop=50 * 48000)
    sf.write(D / "voz.wav", x.astype(np.float32), sr, subtype="FLOAT")
print("ok", sorted(p.name for p in D.iterdir()))
