import numpy as np, pandas as pd
from load import load, power, odds3
D = load()
print("matchs:", len(D), "| avec Pinnacle avant-match:", D.PSH.notna().sum(), "| clôture:", D.PSCH.notna().sum())
# marges moyennes
for p in ["PS","PSC","B365","BW","Avg","Max"]:
    m = D.apply(lambda r: (lambda o: sum(1/x for x in o) - 1 if o else np.nan)(odds3(r, p)), axis=1)
    print(f"marge moyenne {p:5s}: {m.mean()*100:5.2f} %")
rows = []
for _, r in D.iterrows():
    ps, psc = odds3(r, "PS"), odds3(r, "PSC")
    if not ps: continue
    fair = power(ps); fairc = power(psc) if psc else None
    books = {b: odds3(r, b) for b in ["B365","BW"]}
    rows.append((r.lg, r.season, r.res, fair, fairc, books))
print("matchs testés:", len(rows))
def run(sel, thr, haircut=1.0, maxo=6, minp=0.2):
    rets, clvs, kel = [], [], []
    for lg, s, res, fair, fairc, books in rows:
        best = None
        for i in range(3):
            o = max([b[i] for k, b in books.items() if b and k in sel] or [0]) * haircut
            if o <= 1: continue
            p = fair[i]; e = p*o - 1
            if e >= thr and o <= maxo and p >= minp:
                kf = e/(o-1)
                if not best or kf > best[3]: best = (i, o, p, kf)
        if best:
            i, o, p, kf = best
            rets.append(o - 1 if res == i else -1)
            if fairc is not None: clvs.append(o*fairc[i] - 1)
            kel.append(kf)
    r = np.array(rets)
    if not len(r): return None
    ci = 1.96 * r.std(ddof=1) / np.sqrt(len(r))
    return len(r), r.mean(), ci, (np.mean(clvs) if clvs else np.nan)
print("\nStratégie « paris dorés » : miser quand cote bookmaker × probabilité Pinnacle (sans marge) ≥ 1 + seuil, mise fixe 1 unité")
print(f"{'comptes':14s} {'seuil':>5s} {'décote':>6s} {'paris':>6s} {'rendement':>10s} {'± (95 %)':>9s} {'CLV moyen':>9s}")
for sel in [("B365",), ("BW",), ("B365","BW")]:
    for thr in [0.02, 0.03, 0.04, 0.06]:
        for hc in [1.0, 0.985, 0.97]:
            x = run(sel, thr, hc)
            if x: print(f"{'+'.join(sel):14s} {thr*100:4.0f}% {(1-hc)*100:5.1f}% {x[0]:6d} {x[1]*100:9.2f}% {x[2]*100:8.2f}% {x[3]*100:8.2f}%")
