import numpy as np, pandas as pd, math, json
from load import power
D = pd.read_pickle("model.pkl").reset_index(drop=True)
G = 9; RHO = -0.10
fac = np.array([math.factorial(i) for i in range(G+1)], float); I = np.arange(G+1)
pois = lambda l: np.exp(-l) * l**I / fac
d = np.subtract.outer(I, I); t = np.add.outer(I, I)
def ft(lh, la):
    M = np.outer(pois(lh), pois(la)); M[0,0] *= 1-lh*la*RHO; M[0,1] *= 1+lh*RHO; M[1,0] *= 1+la*RHO; M[1,1] *= 1-RHO; return M/M.sum()
# marchés candidats des paris mis en avant (mêmes que l'application) : (probabilité sur la grille, condition sur le score)
MK = {
 "1": (lambda M: M[d>0].sum(), lambda h,a: h>a), "2": (lambda M: M[d<0].sum(), lambda h,a: a>h),
 "1N": (lambda M: M[d>=0].sum(), lambda h,a: h>=a), "N2": (lambda M: M[d<=0].sum(), lambda h,a: h<=a), "12": (lambda M: M[d!=0].sum(), lambda h,a: h!=a),
 "O15": (lambda M: M[t>1].sum(), lambda h,a: h+a>1), "O25": (lambda M: M[t>2].sum(), lambda h,a: h+a>2), "U25": (lambda M: M[t<3].sum(), lambda h,a: h+a<3), "U35": (lambda M: M[t<4].sum(), lambda h,a: h+a<4),
 "BY": (lambda M: M[1:,1:].sum(), lambda h,a: h>0 and a>0), "BN": (lambda M: 1-M[1:,1:].sum(), lambda h,a: not(h>0 and a>0)),
 "HM1_1": (lambda M: M[d>=2].sum(), lambda h,a: h-a>=2), "HP1_2": (lambda M: M[d<=-2].sum(), lambda h,a: a-h>=2),
 "HM2_2": (lambda M: M[d<=1].sum(), lambda h,a: h-a<=1), "HP2_1": (lambda M: M[d>=-1].sum(), lambda h,a: h-a>=-1),
 "HO05": (lambda M: M[1:,:].sum(), lambda h,a: h>=1), "AO05": (lambda M: M[:,1:].sum(), lambda h,a: a>=1),
 "HO15": (lambda M: M[2:,:].sum(), lambda h,a: h>=2), "AO15": (lambda M: M[:,2:].sum(), lambda h,a: a>=2),
 "W1BY": (lambda M: M[(d>0)&(I[None,:]>0)].sum(), lambda h,a: h>a and a>0), "W2BY": (lambda M: M[(d<0)&(I[:,None]>0)].sum(), lambda h,a: a>h and h>0),
 "W1O25": (lambda M: M[(d>0)&(t>2)].sum(), lambda h,a: h>a and h+a>2), "W2O25": (lambda M: M[(d<0)&(t>2)].sum(), lambda h,a: a>h and h+a>2),
 "BYO25": (lambda M: M[1:,1:][t[1:,1:]>2].sum(), lambda h,a: h>0 and a>0 and h+a>2),
 "CS1": (lambda M: M[1:,0].sum(), lambda h,a: h>0 and a==0), "CS2": (lambda M: M[0,1:].sum(), lambda h,a: a>0 and h==0),
 "NC1": (lambda M: M[:,0].sum(), lambda h,a: a==0), "NC2": (lambda M: M[0,:].sum(), lambda h,a: h==0),
}
HCP = {"HM1_1":"h","HP1_2":"a","HM2_2":"h","HP2_1":"a"}
rows = []
for r in D.itertuples():
    M = ft(r.lh, r.la); fav = "h" if r.pH >= r.pA else "a"
    pm = {k: f(M) for k, (f, w) in MK.items() if not (k in HCP and HCP[k] != fav)}
    fb = power([r.B365H, r.B365D, r.B365A]); mk = {"1": fb[0], "2": fb[2], "1N": fb[0]+fb[1], "N2": fb[1]+fb[2], "12": fb[0]+fb[2]}
    try:
        ou = power([float(getattr(r, "_57")), float(getattr(r, "_58"))])
    except Exception: ou = None
    o25 = D.at[r.Index, "B365>2.5"] if "B365>2.5" in D.columns else np.nan; u25 = D.at[r.Index, "B365<2.5"] if "B365<2.5" in D.columns else np.nan
    if o25 == o25 and u25 == u25 and o25 > 1 and u25 > 1:
        q = power([o25, u25]); mk["O25"], mk["U25"] = q[0], q[1]
    odds = {"1": r.B365H, "2": r.B365A, "1N": 0.97/(1/r.B365H+1/r.B365D), "N2": 0.97/(1/r.B365D+1/r.B365A), "12": 0.97/(1/r.B365H+1/r.B365A)}
    if o25 == o25 and o25 > 1: odds["O25"], odds["U25"] = o25, u25
    rows.append(dict(season=r.season, pm=pm, mk=mk, odds=odds, h=r.FTHG, a=r.FTAG))
SEAS = sorted(D.season.unique())
def factors(train):
    f = {}
    for k in MK:
        hit = exp = 0.0
        for x in train:
            p = x["pm"].get(k)
            if p is not None and p >= 0.7: exp += p; hit += MK[k][1](x["h"], x["a"])
        f[k] = min(1, (hit+10)/(exp+10))
    for _ in range(2):
        agg = {}
        for x in train:
            b = pick(x, f)
            if b and b[1] >= 0.75:
                a = agg.setdefault(b[0], [0,0]); a[0] += b[1]; a[1] += MK[b[0]][1](x["h"], x["a"])
        for k, (e, h) in agg.items(): f[k] *= min(1, (h+10)/(e+10))
    return f
def pick(x, f):
    c = []
    for k, p in x["pm"].items():
        pc = p * f.get(k, 1); pk = x["mk"].get(k); c.append((k, pc if pk is None else (pc+pk)/2))
    wins = [z for z in c if z[0] in ("1","2") and z[1] >= 0.70]
    return max(wins, key=lambda z: z[1]) if wins else max(c, key=lambda z: z[1])
def safe(b): return b[1] >= (0.70 if b[0] in ("1","2") else 0.80)
def evaluate(test, f):
    n = hit = 0; sp = 0.0; per = {}; roi = []
    for x in test:
        b = pick(x, f)
        if not safe(b): continue
        w = MK[b[0]][1](x["h"], x["a"]); n += 1; hit += w; sp += b[1]
        q = per.setdefault(b[0], [0,0,0.0]); q[0] += 1; q[1] += w; q[2] += b[1]
        if b[0] in x["odds"]: roi.append(x["odds"][b[0]] - 1 if w else -1)
    return n, hit, sp, per, roi
print("Saison testée | règle hors échantillon (corrections apprises sur les saisons d'avant) | règle de l'application (corrections apprises sur la saison elle-même)")
tot_o = [0,0,0.0]; tot_i = [0,0,0.0]; per_all = {}; roi_all = []
for i, s in enumerate(SEAS):
    test = [x for x in rows if x["season"] == s]
    if i == 0: continue
    f_out = factors([x for x in rows if x["season"] < s]); f_in = factors(test)
    a = evaluate(test, f_out); b = evaluate(test, f_in)
    for T, v in ((tot_o, a), (tot_i, b)): T[0] += v[0]; T[1] += v[1]; T[2] += v[2]
    for k, q in a[3].items(): z = per_all.setdefault(k, [0,0,0.0]); z[0] += q[0]; z[1] += q[1]; z[2] += q[2]
    roi_all += a[4]
    print(f"{s}: hors échantillon {a[1]}/{a[0]} = {a[1]/a[0]*100:.1f} % (annoncé {a[2]/a[0]*100:.1f}) | même saison {b[1]}/{b[0]} = {b[1]/b[0]*100:.1f} % (annoncé {b[2]/b[0]*100:.1f})")
print(f"TOTAL hors échantillon : {tot_o[1]}/{tot_o[0]} = {tot_o[1]/tot_o[0]*100:.1f} % pour {tot_o[2]/tot_o[0]*100:.1f} % annoncé")
print(f"TOTAL même saison     : {tot_i[1]}/{tot_i[0]} = {tot_i[1]/tot_i[0]*100:.1f} % pour {tot_i[2]/tot_i[0]*100:.1f} % annoncé")
print("Par type (hors échantillon) :")
for k, (n, h, sp) in sorted(per_all.items(), key=lambda z: -z[1][0]): print(f"   {k:6s} {n:5d} paris · réussi {h/n*100:5.1f} % · annoncé {sp/n*100:5.1f} %")
r = np.array(roi_all); print(f"Rendement des paris verts cotés (Bet365, doubles chances déduites) : {r.mean()*100:+.1f} % sur {len(r)} paris")
f_all = factors(rows); json.dump({k: round(v, 4) for k, v in f_all.items()}, open("hist_factors.json", "w")); print("facteurs 7 saisons :", {k: round(v,3) for k, v in f_all.items()})
