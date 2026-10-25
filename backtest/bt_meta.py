import numpy as np, pandas as pd, math, unicodedata, datetime as dt
D = pd.read_pickle("model.pkl")   # 10 510 matchs avec prédiction du modèle (mêmes matchs que le test de Fiabilité)
def uk_to_utc(day, hm):
    y = day.year
    def last_sun(m):
        d = dt.date(y, m + 1, 1) - dt.timedelta(days=1) if m < 12 else dt.date(y, 12, 31)
        return dt.datetime(d.year, d.month, d.day - (d.weekday() + 1) % 7, 1)
    t = dt.datetime(day.year, day.month, day.day, int(hm[:2]), int(hm[3:5]))
    bst = last_sun(3) <= t < last_sun(10)
    return t - dt.timedelta(hours=1 if bst else 0)
def sky(utc):
    jd = (utc - dt.datetime(1970,1,1)).total_seconds()/86400 + 2440587.5; d = jd - 2451545.0
    L = 218.316 + 13.176396*d; M = 134.963 + 13.064993*d
    moon = (L + 6.289*math.sin(math.radians(M))) % 360
    g = 357.528 + 0.9856003*d; sun = (280.460 + 0.9856474*d + 1.915*math.sin(math.radians(g)) + 0.020*math.sin(math.radians(2*g))) % 360
    return moon, ((moon - sun) % 360) < 180
EL = ["Feu","Terre","Air","Eau"]*3
def astro(utc):
    moon, wax = sky(utc); el = EL[int(moon//30)]
    return "1" if el == "Feu" else "2" if el == "Air" else "N" if el == "Terre" else ("1" if wax else "2")
def red(n):
    while n > 9: n = sum(int(c) for c in str(n))
    return n or 9
def namenum(s):
    s = unicodedata.normalize("NFD", s); s = "".join(c for c in s if c.isascii() and c.isalpha()).upper()
    return red(sum((ord(c)-65) % 9 + 1 for c in s))
def numero(day, h, a):
    dn = red(sum(int(c) for c in day.strftime("%Y%m%d"))); dh, da = abs(namenum(h)-dn), abs(namenum(a)-dn)
    return "1" if dh < da else "2" if da < dh else "N"
def fnv(s):
    h = 2166136261
    for c in s: h ^= ord(c); h = (h * 16777619) & 0xffffffff
    return h
HOME, AWAY = {1,3,4,7,11,17,19,21}, {0,12,13,15,16,18}
def carto(lg, h, a, day):
    i = fnv(f"v1 · 25/10/2026|{lg}|{h}|{a}|{day.strftime('%Y-%m-%d')}") % 22
    return "1" if i in HOME else "2" if i in AWAY else "N"
res = {"astro":[], "numero":[], "carto":[], "model":[], "home":[]}
for r in D.itertuples():
    out = "1" if r.res == 0 else "N" if r.res == 1 else "2"
    hm = r.Time if isinstance(r.Time, str) and len(r.Time) >= 5 else "15:00"
    utc = uk_to_utc(r.date, hm)
    res["astro"].append(astro(utc) == out); res["numero"].append(numero(r.date, r.HomeTeam, r.AwayTeam) == out)
    res["carto"].append(carto(r.lg, r.HomeTeam, r.AwayTeam, r.date) == out)
    res["model"].append(["1","N","2"][int(np.argmax([r.pH, r.pD, r.pA]))] == out); res["home"].append(out == "1")
from math import erf, sqrt
for k, v in res.items():
    v = np.array(v); n = len(v); h = v.sum(); z = (h - n/3)/sqrt(n*(1/3)*(2/3)); p = 0.5*(1-erf(z/sqrt(2)))
    print(f"{k:7s} {h}/{n} = {h/n*100:.1f} %  (z = {z:+.2f}, p unilatéral = {p:.3f})")
# même astro/numéro/carto : réussite selon la prédiction faite (pour voir si une issue est simplement plus fréquente)
print("\nAvec la bonne référence (hasard qui prédit dans les mêmes proportions que la méthode) :")
outs = np.array(["1" if r == 0 else "N" if r == 1 else "2" for r in D.res])
freq = {k: (outs == k).mean() for k in "1N2"}
print("fréquences réelles :", {k: round(v*100,1) for k, v in freq.items()})
preds = {"astro": [], "numero": [], "carto": []}
for r in D.itertuples():
    hm = r.Time if isinstance(r.Time, str) and len(r.Time) >= 5 else "15:00"; utc = uk_to_utc(r.date, hm)
    preds["astro"].append(astro(utc)); preds["numero"].append(numero(r.date, r.HomeTeam, r.AwayTeam)); preds["carto"].append(carto(r.lg, r.HomeTeam, r.AwayTeam, r.date))
for k, pr in preds.items():
    pr = np.array(pr); n = len(pr); h = (pr == outs).sum(); exp = sum((pr == c).mean() * freq[c] for c in "1N2")
    z = (h - n*exp) / sqrt(n*exp*(1-exp)); p = 0.5*(1-erf(z/sqrt(2)))
    mix = {c: round((pr == c).mean()*100) for c in "1N2"}
    print(f"{k:7s} réussi {h/n*100:.1f} % · hasard équivalent {exp*100:.1f} % · écart {(h/n-exp)*100:+.1f} pts · p = {p:.2f} · prédit 1/N/2 = {mix}")
print("\nNumérologie : d'où vient l'écart ?")
rng = np.random.default_rng(1)
days = np.array([red(sum(int(c) for c in d.strftime("%Y%m%d"))) for d in D.date])
nh = np.array([namenum(x) for x in D.HomeTeam]); na = np.array([namenum(x) for x in D.AwayTeam])
def acc(dn):
    dh, da = abs(nh-dn), abs(na-dn); pr = np.where(dh < da, "1", np.where(da < dh, "2", "N")); return (pr == outs).mean()
real = acc(days); sh = [acc(rng.permutation(days)) for _ in range(300)]
print(f"réel {real*100:.2f} % · nombres du jour mélangés au hasard : moyenne {np.mean(sh)*100:.2f} % (95 % des tirages entre {np.percentile(sh,2.5)*100:.2f} et {np.percentile(sh,97.5)*100:.2f})")
# saison par saison
for s, g in D.groupby("season"):
    idx = g.index.values; print(s, f"{(np.where(abs(nh[idx]-days[idx]) < abs(na[idx]-days[idx]), '1', np.where(abs(na[idx]-days[idx]) < abs(nh[idx]-days[idx]), '2', 'N')) == outs[idx]).mean()*100:.1f} %")
