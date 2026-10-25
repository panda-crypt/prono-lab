import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, glob, os
LG = {"E0":"Premier League","SP1":"Liga","I1":"Serie A","D1":"Bundesliga","F1":"Ligue 1"}
SEAS = ["1920","2021","2122","2223","2324","2425","2526"]
def load(seasons=SEAS):
    out = []
    for s in seasons:
        for l in LG:
            f = f"data/{l}_{s}.csv"
            if not os.path.exists(f): continue
            d = pd.read_csv(f, encoding="utf-8-sig", on_bad_lines="skip")
            d = d.dropna(subset=["HomeTeam","AwayTeam","FTHG","FTAG"])
            d["lg"] = l; d["season"] = s
            d["date"] = pd.to_datetime(d["Date"], dayfirst=True, errors="coerce")
            out.append(d)
    D = pd.concat(out, ignore_index=True).sort_values("date").reset_index(drop=True)
    D["FTHG"] = D.FTHG.astype(int); D["FTAG"] = D.FTAG.astype(int)
    D["res"] = np.where(D.FTHG > D.FTAG, 0, np.where(D.FTHG == D.FTAG, 1, 2))
    return D
def power(o):
    """Marge retirée, méthode « power » (identique à l'application)."""
    o = np.asarray(o, float); inv = 1/o
    if inv.sum() <= 1: return inv/inv.sum()
    lo, hi = 1.0, 4.0
    for _ in range(60):
        k = (lo+hi)/2
        if (inv**k).sum() > 1: lo = k
        else: hi = k
    return inv**((lo+hi)/2)
def odds3(row, p):
    try:
        o = [float(row[p+"H"]), float(row[p+"D"]), float(row[p+"A"])]
        return o if all(x > 1 for x in o) else None
    except (KeyError, ValueError, TypeError): return None
