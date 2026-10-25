import numpy as np, pandas as pd, math
from load import load, power, odds3
D = load()
D = D[D.PSH.notna() & D.PSCH.notna() & D.B365H.notna()].reset_index(drop=True)
MAXG = 10; RHO = -0.10; DECAY = 0.88   # comme l'application (récence : facteur 0,88 par journée d'écart approx.)
fact = [math.factorial(i) for i in range(MAXG+1)]
def matrix(lh, la):
    i = np.arange(MAXG+1)
    ph = np.exp(-lh) * lh**i / np.array(fact); pa = np.exp(-la) * la**i / np.array(fact)
    M = np.outer(ph, pa)
    M[0,0] *= 1 - lh*la*RHO; M[0,1] *= 1 + lh*RHO; M[1,0] *= 1 + la*RHO; M[1,1] *= 1 - RHO
    return M / M.sum()
def ratings(hist, teams, ref_date):
    # forces attaque/défense pondérées par la récence (en semaines), ajustées 3 fois selon la force des adversaires
    w = DECAY ** ((ref_date - hist.date).dt.days.values / 7.0)
    hg, ag = hist.FTHG.values, hist.FTAG.values
    mu_h = np.average(hg, weights=w); mu_a = np.average(ag, weights=w)
    idx = {t:i for i,t in enumerate(teams)}; hi = np.array([idx[t] for t in hist.HomeTeam]); ai = np.array([idx[t] for t in hist.AwayTeam])
    att = np.ones(len(teams)); de = np.ones(len(teams))
    for _ in range(3):
        na = np.zeros(len(teams)); da = np.zeros(len(teams)); nd = np.zeros(len(teams)); dd = np.zeros(len(teams))
        np.add.at(na, hi, w*hg); np.add.at(da, hi, w*mu_h*de[ai]); np.add.at(na, ai, w*ag); np.add.at(da, ai, w*mu_a*de[hi])
        np.add.at(nd, hi, w*ag); np.add.at(dd, hi, w*mu_a*att[ai]); np.add.at(nd, ai, w*hg); np.add.at(dd, ai, w*mu_h*att[hi])
        att = (na + 6) / (da + 6); de = (nd + 6) / (dd + 6)     # régularisation vers 1 (équivalent de 6 buts)
    return att, de, mu_h, mu_a, idx
out = []
for (lg, s), G in D.groupby(["lg","season"], sort=False):
    prev = D[(D.lg == lg) & (D.season < s)]
    for dt, day in G.groupby("date"):
        hist = pd.concat([prev[prev.date > dt - pd.Timedelta(days=300)], G[G.date < dt]])
        if len(G[G.date < dt]) < 30: continue                  # début de saison : pas assez de matchs
        teams = sorted(set(hist.HomeTeam) | set(hist.AwayTeam) | set(day.HomeTeam) | set(day.AwayTeam))
        att, de, mh, ma, idx = ratings(hist, teams, dt)
        for _, r in day.iterrows():
            h, a = idx[r.HomeTeam], idx[r.AwayTeam]
            M = matrix(mh*att[h]*de[a], ma*att[a]*de[h])
            d = np.subtract.outer(np.arange(MAXG+1), np.arange(MAXG+1)); t = np.add.outer(np.arange(MAXG+1), np.arange(MAXG+1))
            out.append(dict(i=r.name, lh=mh*att[h]*de[a], la=ma*att[a]*de[h], pH=M[d>0].sum(), pD=M[d==0].sum(), pA=M[d<0].sum(), o15=M[t>1].sum(), o25=M[t>2].sum(), u35=M[t<4].sum(),
                            by=M[1:,1:].sum(), hm1=M[d>=2].sum(), am1=M[d<=-2].sum(), hp2=M[d>=-1].sum(), ap2=M[d<=1].sum()))
P = pd.DataFrame(out).set_index("i")
D = D.join(P, how="inner")
D.to_pickle("model.pkl")  # utilisé par bt_tickets.py, bt_markets.py, bt_green_oos.py, bt_meta.py
print("matchs avec prédiction du modèle :", len(D))
