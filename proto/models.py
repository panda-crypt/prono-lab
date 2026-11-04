"""Prototype : nouveaux modèles des coupes d'Europe, testés de façon chronologique.

Entrées (produites par harness.js) :
  cur.json  : prédictions du modèle européen actuel (données actuelles de l'application)
  feat.json : variables de chaque club au jour du match, avec les 25 clubs reliés à leur championnat national
  hist_odds.json : cotes 1N2 retrouvées dans l'historique git de raw/euro.py

Modèles :
  A : notation européenne unique. Force = a*pays + b*exp(c*pays)*note nationale (+ effet club appris en coupe d'Europe).
      Le terme exp(c*pays) pondère la note nationale par le niveau du championnat (c > 0 : dominer un petit championnat compte moins).
  B : mélange de A et du modèle actuel, proportion apprise sur les matchs déjà joués.
  C : A + ajustements : tendance aux buts (attaque + défense nationales) et forme (écart de buts moyen sur 5 matchs nationaux).
Chaque jour de match, les paramètres sont réappris uniquement sur les matchs européens antérieurs.
"""
import json, math, sys
import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson

D = sys.argv[1] if len(sys.argv) > 1 else "."
cur = {(r["lg"], r["h"], r["a"], r["d"]): r for r in json.load(open(f"{D}/cur.json"))["recs"]}
F = json.load(open(f"{D}/feat.json"))
recs = F["recs"]
odds = json.load(open(f"{D}/hist_odds.json"))
logs = [math.log(v) for v in F["coef"].values()]
ML = sum(logs) / len(logs)
RHO, MAXG = -0.10, 10

def matrix(lh, la):
    lh = min(5, max(0.15, lh)); la = min(5, max(0.15, la))
    i = np.arange(MAXG + 1)
    M = np.outer(poisson.pmf(i, lh), poisson.pmf(i, la))
    M[0, 0] *= 1 - lh * la * RHO; M[0, 1] *= 1 + lh * RHO; M[1, 0] *= 1 + la * RHO; M[1, 1] *= 1 - RHO
    M /= M.sum()
    pH = np.tril(M, -1).sum(); pA = np.triu(M, 1).sum(); pD = 1 - pH - pA
    tot = i[:, None] + i[None, :]
    return np.array([pH, pD, pA]), M[tot > 2].sum()

def z(c): return math.log(c["coef"]) - ML
def r(c):  # note nationale (log attaque - log défense), None si championnat non suivi
    d = c["dom"]; return None if d is None else d["att"] - d["def"]
def t(c):  # tendance aux buts du club dans son championnat
    d = c["dom"]; return 0.0 if d is None else (d["att"] + d["def"]) / 2
def fm(c):
    d = c["dom"]; return 0.0 if d is None or d["formGd"] is None else d["formGd"]

PRI = {  # moyenne, écart-type des a priori
    "m": (math.log(1.45), 0.2), "h": (0.12, 0.08), "a": (0.45, 0.3), "b": (0.8, 0.3), "c": (0.0, 0.5),
    "kU": (0.0, 0.4), "kC": (0.0, 0.4), "tau": (0.0, 0.3), "phi": (0.0, 0.1),
}
TAU_U = 0.3

def strength(P, c, comp, uidx, u):
    rr = r(c)
    base = P["a"] * z(c) + (P["b"] * math.exp(P["c"] * z(c)) * rr if rr is not None else (P["kU"] if comp == "ucl" else P["kC"] if comp == "uecl" else 0.0))
    return base + (u[uidx[c["id"]]] if c["id"] in uidx else 0.0)

def lambdas(P, x, uidx, u, full):
    sH = strength(P, x["H"], x["lg"], uidx, u); sA = strength(P, x["A"], x["lg"], uidx, u)
    d = (sH - sA) / 2
    g = 0.0
    if full:
        g = P["tau"] * (t(x["H"]) + t(x["A"]))
        d += P["phi"] * (fm(x["H"]) - fm(x["A"])) / 2
    return math.exp(P["m"] + P["h"] + d + g), math.exp(P["m"] - P["h"] - d + g)

def fit(train, full):
    keys = list(PRI) if full else [k for k in PRI if k not in ("tau", "phi")]
    clubs = sorted({x["h"] for x in train} | {x["a"] for x in train}); uidx = {c: i for i, c in enumerate(clubs)}
    nk = len(keys)
    def unpack(v):
        P = {k: v[i] for i, k in enumerate(keys)}
        for k in PRI: P.setdefault(k, 0.0)
        return P, v[nk:]
    def nlp(v):
        P, u = unpack(v)
        s = sum(((P[k] - PRI[k][0]) / PRI[k][1]) ** 2 / 2 for k in keys) + float(np.sum(u ** 2)) / (2 * TAU_U ** 2)
        for x in train:
            lh, la = lambdas(P, x, uidx, u, full)
            gh, ga = x["s"]
            s -= gh * math.log(lh) - lh + ga * math.log(la) - la
        return s
    v0 = np.array([PRI[k][0] for k in keys] + [0.0] * len(clubs))
    res = minimize(nlp, v0, method="L-BFGS-B", options={"maxiter": 3000})
    P, u = unpack(res.x)
    return P, uidx, u

def out(s): return 0 if s[0] > s[1] else 1 if s[0] == s[1] else 2
def brier(p, o): return float(sum((p[i] - (i == o)) ** 2 for i in range(3)))
def ll(p, o): return -math.log(max(1e-9, p[o]))

days = sorted({x["d"][:10] for x in recs if x["ev"]})
res = {k: [] for k in ("cur", "lien", "A", "B", "C")}
mk = []      # (index dans res, probas marché)
params = []
wB = 0.5
for day in days:
    train = [x for x in recs if x.get("s") and x["d"] < day + "T00:00"]
    PA = fit(train, False); PC = fit(train, True)
    params.append((day, {k: round(v, 3) for k, v in PA[0].items() if k in ("a", "b", "c", "h", "m")}, {k: round(PC[0][k], 3) for k in ("tau", "phi")}))
    # proportion du mélange B : apprise sur les matchs déjà évalués (log-loss), 0,5 au départ
    if res["A"]:
        best = None
        for w in np.linspace(0, 1, 21):
            L = sum(ll(w * np.array(a["p"]) + (1 - w) * np.array(c["p"]), a["o"]) for a, c in zip(res["A"], res["cur"]))
            if best is None or L < best[0]: best = (L, w)
        wB = best[1]
    for x in [x for x in recs if x["ev"] and x["d"][:10] == day]:
        o = out(x["s"]); c = cur[(x["lg"], x["h"], x["a"], x["d"])]
        pa, oa = matrix(*lambdas(PA[0], x, PA[1], PA[2], False))
        pc, oc = matrix(*lambdas(PC[0], x, PC[1], PC[2], True))
        pb = wB * pa + (1 - wB) * np.array(c["cur"])
        over = x["s"][0] + x["s"][1] > 2
        for k, p, o25 in (("cur", np.array(c["cur"]), c["curO25"]), ("lien", np.array(x["cur"]), x["curO25"]), ("A", pa, oa), ("B", pb, wB * oa + (1 - wB) * c["curO25"]), ("C", pc, oc)):
            res[k].append({"p": list(map(float, p)), "o": o, "o25": float(o25), "over": over, "m": f'{x["lg"]}|{x["h"]}|{x["a"]}', "d": x["d"], "w": wB})
        key = f'{x["lg"]}|{x["h"]}|{x["a"]}'
        if key in odds:
            q = np.array([1 / v for v in odds[key]["o"]]); mk.append((len(res["cur"]) - 1, q / q.sum()))

rng = np.random.default_rng(1)
def summary(k):
    R = res[k]; n = len(R)
    b = np.array([brier(x["p"], x["o"]) for x in R]); l = np.array([ll(x["p"], x["o"]) for x in R])
    bo = np.mean([(x["o25"] - x["over"]) ** 2 for x in R])
    fav = np.mean([int(np.argmax(x["p"]) == x["o"]) for x in R])
    return n, b.mean(), l.mean(), bo, fav, b
print(f"Matchs évalués : {len(res['cur'])} (chronologique, {len(days)} journées)")
print(f"{'modèle':6} {'Brier 1N2':>10} {'log-loss':>9} {'Brier +2,5':>11} {'favori juste':>13}   écart Brier vs actuel [IC 90 %]")
base = summary("cur")[5]
for k in res:
    n, b, l, bo, fav, arr = summary(k)
    dif = arr - base
    bs = [rng.choice(dif, len(dif)).mean() for _ in range(4000)]
    print(f"{k:6} {b:10.4f} {l:9.4f} {bo:11.4f} {fav:12.0%}   {dif.mean():+.4f} [{np.percentile(bs,5):+.4f} ; {np.percentile(bs,95):+.4f}]")
print("\nParamètres appris (dernier jour) A :", params[-1][1], "· C :", params[-1][2], "· mélange B : part de A =", res["B"][-1]["w"])
for p in params: print("  ", p)
if mk:
    print(f"\nSous-ensemble avec cotes retrouvées : {len(mk)} matchs")
    mb = np.mean([brier(q, res['cur'][i]['o']) for i, q in mk]); print(f"  marché  Brier {mb:.4f}")
    for k in res: print(f"  {k:6}  Brier {np.mean([brier(res[k][i]['p'], res[k][i]['o']) for i, q in mk]):.4f}")
json.dump({k: v for k, v in res.items()}, open(f"{D}/results.json", "w"))

# Prochains matchs (4 et 5/11) : modèles appris sur les 153 matchs joués, comparés aux cotes relevées le 31/10
played = [x for x in recs if x.get("s")]
PA = fit(played, False); PC = fit(played, True)
up = [x for x in recs if x.get("up")]
print(f"\nProchains matchs avec cotes ({sum(1 for x in up if x['lg']+'|'+x['h']+'|'+x['a'] in odds)} sur {len(up)}) : victoire domicile / nul / victoire extérieur, en %")
gap = {k: [] for k in ("cur", "lien", "A", "C")}
for x in up:
    key = x["lg"] + "|" + x["h"] + "|" + x["a"]
    if key not in odds: continue
    q = np.array([1 / v for v in odds[key]["o"]]); q /= q.sum()
    c = cur[(x["lg"], x["h"], x["a"], x["d"])]
    P = {"cur": np.array(c["cur"]), "lien": np.array(x["cur"]), "A": matrix(*lambdas(PA[0], x, PA[1], PA[2], False))[0], "C": matrix(*lambdas(PC[0], x, PC[1], PC[2], True))[0]}
    f = lambda p: "/".join(f"{100*v:.0f}" for v in p)
    print(f"  {x['h'][:16]:16} - {x['a'][:16]:16} marché {f(q):9} actuel {f(P['cur']):9} lien {f(P['lien']):9} A {f(P['A']):9} C {f(P['C']):9}")
    for k in gap: gap[k].append(np.abs(P[k] - q).sum() / 2)
print("  Écart moyen au marché (points de probabilité) : " + ", ".join(f"{k} {100*np.mean(v):.1f}" for k, v in gap.items()))
