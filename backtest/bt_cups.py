"""Écart de niveau entre divisions, pour les coupes nationales (constante DIV_GAP de l'application).

Méthode : la note d'une équipe sur une saison est r = log(buts marqués / buts encaissés) dans son championnat
(0 = équipe moyenne de ce championnat). Pour les équipes qui restent dans le même championnat, la note de la saison
suivante vaut en moyenne beta × la note de la saison (retour vers la moyenne : chance, effectif qui change).
Une équipe promue garde sa force réelle mais affronte des adversaires plus forts : sa note attendue est
beta × r_avant − écart ; une équipe reléguée : beta × r_avant + écart. L'écart est la moyenne des deux mesures
(promues et reléguées), ce qui neutralise le biais de sélection (les promues ont souvent eu de la chance, les
reléguées de la malchance, et beta corrige ce retour vers la moyenne).

  cd backtest && python3 bt_cups.py      (fichiers de backtest/data, voir README)
"""
import csv, math, pathlib, statistics as st
DATA = pathlib.Path(__file__).parent / "data"
SEASONS = ["1920", "2021", "2122", "2223", "2324", "2425", "2526"]
TIERS = {"ENG": ["E0", "E1", "E2", "E3"], "ESP": ["SP1", "SP2"], "ITA": ["I1", "I2"], "GER": ["D1", "D2"], "FRA": ["F1", "F2"]}

def season_ratings(code, s):
    f = DATA / f"{code}_{s}.csv"
    if not f.exists(): return {}
    tot = {}
    with open(f, encoding="utf-8-sig", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh):
            if not r.get("HomeTeam") or r.get("FTHG", "") in ("", None): continue
            h, a, hg, ag = r["HomeTeam"].strip(), r["AwayTeam"].strip(), int(float(r["FTHG"])), int(float(r["FTAG"]))
            for t, f_, a_ in ((h, hg, ag), (a, ag, hg)):
                x = tot.setdefault(t, [0, 0, 0]); x[0] += 1; x[1] += f_; x[2] += a_
    return {t: math.log((v[1] + 0.5) / (v[2] + 0.5)) for t, v in tot.items() if v[0] >= 20}

R = {}   # (code, saison) -> {équipe: note}
for c, codes in TIERS.items():
    for code in codes:
        for s in SEASONS: R[(code, s)] = season_ratings(code, s)

# 1) retour vers la moyenne, mesuré sur les équipes qui restent dans le même championnat
num = den = 0.0
for codes in TIERS.values():
    for code in codes:
        for s0, s1 in zip(SEASONS, SEASONS[1:]):
            a, b = R[(code, s0)], R[(code, s1)]
            for t in set(a) & set(b): num += a[t] * b[t]; den += a[t] ** 2
beta = num / den
print(f"retour vers la moyenne : beta = {beta:.3f}")

# 2) écart entre deux divisions consécutives d'un même pays
out = {}
for c, codes in TIERS.items():
    for up, low in zip(codes, codes[1:]):
        prom, rel = [], []
        for s0, s1 in zip(SEASONS, SEASONS[1:]):
            lo0, hi1, hi0, lo1 = R[(low, s0)], R[(up, s1)], R[(up, s0)], R[(low, s1)]
            for t in set(lo0) & set(hi1): prom.append(beta * lo0[t] - hi1[t])     # promues
            for t in set(hi0) & set(lo1): rel.append(lo1[t] - beta * hi0[t])      # reléguées
        if not prom or not rel: print(c, up, low, "données manquantes"); continue
        g = (st.mean(prom) + st.mean(rel)) / 2
        se = 0.5 * math.sqrt(st.pvariance(prom) / len(prom) + st.pvariance(rel) / len(rel))
        out[(up, low)] = round(g, 3)
        print(f"{c} {up}->{low} : écart {g:.3f} ± {se:.3f}  (promues {st.mean(prom):.3f}, n={len(prom)} ; reléguées {st.mean(rel):.3f}, n={len(rel)})")
print("DIV_GAP =", {f"{u}>{l}": v for (u, l), v in out.items()})
