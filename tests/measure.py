"""Mediciones para check.py: frecuencia exacta de un tono estable, pista de tono (YIN), formantes (LPC)."""
import numpy as np, soundfile as sf, pathlib
D = pathlib.Path(__file__).parent / "out"; S = pathlib.Path(__file__).parent / "signals"

def load(name, sig=False):
    x, sr = sf.read((S if sig else D) / f"{name}.wav")
    return (x.mean(1) if x.ndim > 1 else x), sr

def cents(a, b): return 1200 * np.log2(a / b)
def midi2f(n, a4=440.0): return a4 * 2 ** ((n - 69) / 12)

def peak_freq(x, sr, t0, t1, near):
    """frecuencia del pico de la FFT (ventana gaussiana, interpolación parabólica en dB) cerca de 'near'"""
    seg = x[int(t0 * sr):int(t1 * sr)]; n = len(seg)
    w = np.exp(-0.5 * ((np.arange(n) - n / 2) / (n / 7)) ** 2)
    N = 1 << int(np.ceil(np.log2(n * 8)))
    X = 20 * np.log10(np.abs(np.fft.rfft(seg * w, N)) + 1e-20); f = np.fft.rfftfreq(N, 1 / sr)
    m = (f > near / 1.12) & (f < near * 1.12); i = np.argmax(np.where(m, X, -1e9))
    a, b, c = X[i - 1], X[i], X[i + 1]; d = 0.5 * (a - c) / (a - 2 * b + c)
    return (i + d) * sr / N

def yin(x, sr, fmin=60, fmax=1200, hop=0.005, thr=0.15):
    """pista de tono: tiempos, f0 (nan sin voz) y aperiodicidad (d' mínimo)"""
    tmax = int(sr / fmin); W = tmax; tmin = int(sr / fmax); N2 = W + tmax
    nf = 1 << int(np.ceil(np.log2(2 * N2)))
    H = int(hop * sr); T, F, A = [], [], []
    cs_all = np.r_[0, np.cumsum(x * x)]
    for st in range(0, len(x) - N2, H):
        fr = x[st:st + N2]
        e0 = cs_all[st + W] - cs_all[st]
        if e0 / W < 1e-7: T.append((st + N2 / 2) / sr); F.append(np.nan); A.append(1); continue
        r = np.fft.irfft(np.conj(np.fft.rfft(fr[:W], nf)) * np.fft.rfft(fr, nf))[:tmax + 2]
        et = cs_all[st + np.arange(tmax + 2) + W] - cs_all[st + np.arange(tmax + 2)]
        d = np.maximum(e0 + et - 2 * r, 0); d[0] = 0
        cm = np.cumsum(d[1:]); dp = np.ones_like(d); dp[1:] = d[1:] * np.arange(1, len(d)) / np.maximum(cm, 1e-20)
        cand = np.where(dp[tmin:tmax] < thr)[0]
        if len(cand):
            t = cand[0] + tmin
            while t + 1 < tmax and dp[t + 1] < dp[t]: t += 1
        else: t = tmin + np.argmin(dp[tmin:tmax])
        a, b, c = dp[t - 1], dp[t], dp[t + 1]; den = a - 2 * b + c
        tt = t + (0.5 * (a - c) / den if den > 0 else 0)
        T.append((st + N2 / 2) / sr); A.append(b); F.append(sr / tt if b < 0.25 else np.nan)
    return np.array(T), np.array(F), np.array(A)

def formants(x, sr, t0, t1, order=10, fs=10000):
    """F1 y F2 (Hz) por LPC sobre cuadros de 40 ms (mediana)"""
    from scipy.signal import resample_poly
    from scipy.linalg import solve_toeplitz
    from math import gcd
    g = gcd(int(sr), fs); y = resample_poly(x[int(t0 * sr):int(t1 * sr)], fs // g, int(sr) // g)
    n = int(0.04 * fs); res = []
    for st in range(0, len(y) - n, n // 2):
        f = y[st:st + n] * np.hamming(n)
        r = np.correlate(f, f, "full")[n - 1:n + order]
        if r[0] <= 0: continue
        a = solve_toeplitz(r[:order], r[1:order + 1])
        roots = np.roots(np.r_[1, -a]); roots = roots[np.imag(roots) > 0]
        fr = np.angle(roots) * fs / (2 * np.pi); bw = -np.log(np.abs(roots)) * fs / np.pi
        ok = sorted(fr[(fr > 250) & (bw < 600)])
        if len(ok) >= 2: res.append(ok[:2])
    return np.median(np.array(res), 0) if res else np.array([np.nan, np.nan])
