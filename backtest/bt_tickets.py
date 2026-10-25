import numpy as np, pandas as pd, math
from load import power
D = pd.read_pickle("model.pkl")
f = lambda r, p: [float(r[p+"H"]), float(r[p+"D"]), float(r[p+"A"])]
D["fairC"] = D.apply(lambda r: power(f(r,"PSC")), axis=1)
D["fairB"] = D.apply(lambda r: power(f(r,"B365")), axis=1)
y = D.res.values
def ll(P): return -np.mean(np.log([p[i] for p, i in zip(P, y)]))
mod = [np.array([a,b,c])/(a+b+c) for a,b,c in zip(D.pH, D.pD, D.pA)]
blend = [0.5*m + 0.5*b for m, b in zip(mod, D.fairB)]
print("== 1. Qualité des probabilités 1N2 (perte logarithmique, plus bas = mieux) ==")
print(f"modèle seul {ll(mod):.4f} | Bet365 sans marge {ll(D.fairB):.4f} | moyenne modèle+Bet365 {ll(blend):.4f} | Pinnacle clôture {ll(D.fairC):.4f}")

print("\n== 2. Valeur selon le modèle seul (mode sans clé : 60 % modèle + 40 % marché, seuil 4 %, cote Bet365) ==")
rets = []; clv = []
for k, r in enumerate(D.itertuples()):
    o = [r.B365H, r.B365D, r.B365A]; mb = r.fairB; m = mod[k]; best = None
    for i in range(3):
        p = 0.6*m[i] + 0.4*mb[i]; e = p*o[i] - 1
        if e >= 0.04 and o[i] <= 6 and m[i] >= 0.2 and m[i] - mb[i] <= 0.08:
            kf = e/(o[i]-1)
            if not best or kf > best[2]: best = (i, o[i], kf)
    if best: rets.append(best[1]-1 if r.res == best[0] else -1); clv.append(best[1]*r.fairC[best[0]] - 1)
r_ = np.array(rets); print(f"{len(r_)} paris, rendement {r_.mean()*100:+.2f} % (± {1.96*r_.std()/np.sqrt(len(r_))*100:.1f}), CLV {np.mean(clv)*100:+.2f} %")

print("\n== 3. Paris verts : l'événement le plus probable de chaque match ==")
# probabilité affichée = moyenne modèle / marché quand le marché cote ce pari (comme l'application)
rows = []
for k, r in enumerate(D.itertuples()):
    fb = r.fairB; m = mod[k]
    ou = [r._asdict().get("B365_2_5"), None]
    try: o25, u25 = float(getattr(r, "_59")), None
    except Exception: pass
    rows.append(None)
# accès simple aux colonnes plus/moins
O25 = D["B365>2.5"].astype(float).values; U25 = D["B365<2.5"].astype(float).values
res = D.res.values; tg = (D.FTHG + D.FTAG).values; dif = (D.FTHG - D.FTAG).values; bt = ((D.FTHG>0)&(D.FTAG>0)).values
picks = []
for k, r in enumerate(D.itertuples()):
    fb = r.fairB; m = mod[k]
    ou_ok = O25[k] > 1 and U25[k] > 1
    fo = power([O25[k], U25[k]]) if ou_ok else None
    fav = "1" if m[0] >= m[2] else "2"
    c = {
      "1": ((m[0]+fb[0])/2, r.B365H, res[k]==0), "2": ((m[2]+fb[2])/2, r.B365A, res[k]==2),
      "1N": ((m[0]+m[1]+fb[0]+fb[1])/2, 0.97/(1/r.B365H+1/r.B365D), res[k]!=2), "N2": ((m[1]+m[2]+fb[1]+fb[2])/2, 0.97/(1/r.B365D+1/r.B365A), res[k]!=0),
      "O15": (r.o15, None, tg[k]>1), "U35": (r.u35, None, tg[k]<4), "BY": (r.by, None, bt[k]), "BN": (1-r.by, None, not bt[k]),
      "O25": (((r.o25+fo[0])/2) if fo is not None else r.o25, O25[k] if ou_ok else None, tg[k]>2),
      "U25": (((1-r.o25+fo[1])/2) if fo is not None else 1-r.o25, U25[k] if ou_ok else None, tg[k]<3),
    }
    if fav == "1": c["HM1"] = (r.hm1, None, dif[k]>=2); c["AP2"] = (r.ap2, None, dif[k]<=1)
    else: c["AM1"] = (r.am1, None, dif[k]<=-2); c["HP2"] = (r.hp2, None, dif[k]>=-1)
    w = [(kk, v) for kk, v in c.items() if kk in ("1","2") and v[0] >= 0.70]
    kk, v = max(w, key=lambda x: x[1][0]) if w else max(c.items(), key=lambda x: x[1][0])
    green = v[0] >= (0.70 if kk in ("1","2") else 0.80)
    picks.append(dict(k=kk, p=v[0], o=v[1], hit=bool(v[2]), green=green, i=k, date=r.date, lg=r.lg, real=kk in ("1","2","O25","U25")))
Pk = pd.DataFrame(picks); G = Pk[Pk.green]
print(f"{len(G)} paris verts sur {len(Pk)} matchs ({len(G)/len(Pk)*100:.0f} %) · annoncé {G.p.mean()*100:.1f} % · réussi {G.hit.mean()*100:.1f} %")
for kk, g in G.groupby("k"): print(f"   {kk:4s} {len(g):5d} paris · annoncé {g.p.mean()*100:5.1f} % · réussi {g.hit.mean()*100:5.1f} %" + (f" · rendement à la cote Bet365 {np.mean(np.where(g.hit, g.o-1, -1))*100:+.1f} %" if g.o.notna().all() else ""))
R = G[G.o.notna()]; print(f"   rendement des paris verts cotés (cote Bet365, doubles chances déduites) : {np.mean(np.where(R.hit, R.o-1, -1))*100:+.2f} % sur {len(R)} paris")
Pk.to_pickle("picks.pkl")

print("\n== 4. Tickets, rejoués chaque semaine (cotes Bet365) ==")
Pk["wk"] = pd.to_datetime(Pk.date).dt.strftime("%G-%V")
D["wk"] = pd.to_datetime(D.date).dt.strftime("%G-%V")
def summary(name, res):
    a = np.array(res)
    if not len(a): print(f"{name}: aucun"); return
    won = (a > 0).mean(); print(f"{name:28s} {len(a):4d} tickets · gagnés {won*100:5.1f} % · rendement {a.mean()*100:+7.1f} % (± {1.96*a.std()/np.sqrt(len(a))*100:.0f})")
T = {n: [] for n in ["Simple le plus sûr","Combiné sûr (2 verts)","Combiné de 3 verts","Combiné de 3 victoires","Grosse cote : 5 victoires","Jackpot ×50","Jackpot ×150","Jackpot ×500"]}
for wk, W in Pk.groupby("wk"):
    g = W[W.green & W.o.notna()].sort_values("p", ascending=False)
    def combo(legs): return (np.prod(legs.o) - 1) if legs.hit.all() else -1
    if len(g) >= 1: T["Simple le plus sûr"].append(combo(g.head(1)))
    if len(g) >= 2: T["Combiné sûr (2 verts)"].append(combo(g.head(2)))
    if len(g) >= 3: T["Combiné de 3 verts"].append(combo(g.head(3)))
    # victoires : favori de chaque match
    wins = []
    for k in W.i:
        r = D.iloc[k]; m = mod[k]; fb = r.fairB
        for j, oc in ((0, r.B365H), (2, r.B365A)):
            p = (m[j]+fb[j])/2
            if p >= 0.5: wins.append(dict(p=p, o=oc, hit=r.res==j))
    wins = pd.DataFrame(wins)
    if len(wins) >= 3: T["Combiné de 3 victoires"].append(combo(wins.sort_values("p", ascending=False).head(3)))
    if len(wins) >= 5: T["Grosse cote : 5 victoires"].append(combo(wins.sort_values("p", ascending=False).head(5)))
    # jackpots : favoris >= 45 % (prob. prudente = min modèle / marché), sélection la plus efficace
    jp = []
    for k in W.i:
        r = D.iloc[k]; m = mod[k]; fb = r.fairB
        j = 0 if m[0] >= m[2] else 2; p = min(m[j], fb[j]); o = r.B365H if j == 0 else r.B365A
        if p >= 0.45 and 1.2 <= o <= 4: jp.append(dict(p=p, o=o, hit=r.res==j, eff=math.log(1/p)/math.log(o)))
    jp = sorted(jp, key=lambda x: x["eff"])
    for tgt, name in ((50,"Jackpot ×50"),(150,"Jackpot ×150"),(500,"Jackpot ×500")):
        legs, O = [], 1
        for x in jp:
            if O >= tgt or len(legs) >= 16: break
            legs.append(x); O *= x["o"]
        if O >= tgt*0.8: T[name].append(O-1 if all(x["hit"] for x in legs) else -1)
for n, v in T.items(): summary(n, v)
