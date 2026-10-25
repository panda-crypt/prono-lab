import numpy as np, pandas as pd, math
D = pd.read_pickle("model.pkl"); D = D[D.HTHG.notna()].reset_index(drop=True)
G = 8; RHO = -0.10; SH = 0.447
fac = np.array([math.factorial(i) for i in range(G+1)], float); I = np.arange(G+1)
pois = lambda l: np.exp(-l) * l**I / fac
def ft(lh, la):
    M = np.outer(pois(lh), pois(la)); M[0,0] *= 1-lh*la*RHO; M[0,1] *= 1+lh*RHO; M[1,0] *= 1+la*RHO; M[1,1] *= 1-RHO; return M/M.sum()
d = np.subtract.outer(I, I); t = np.add.outer(I, I)
MK = {  # nom: (fonction de probabilité sur la grille, condition sur le score)
 "DNB1 (hors nul)": (lambda M: M[d>0].sum()/(1-M[d==0].sum()), lambda h,a,hh,ha: h>a, lambda h,a: h!=a),
 "DNB2 (hors nul)": (lambda M: M[d<0].sum()/(1-M[d==0].sum()), lambda h,a,hh,ha: a>h, lambda h,a: h!=a),
 "Domicile marque": (lambda M: M[1:,:].sum(), lambda h,a,hh,ha: h>=1, None),
 "Extérieur marque": (lambda M: M[:,1:].sum(), lambda h,a,hh,ha: a>=1, None),
 "Domicile +1,5 but": (lambda M: M[2:,:].sum(), lambda h,a,hh,ha: h>=2, None),
 "Extérieur +1,5 but": (lambda M: M[:,2:].sum(), lambda h,a,hh,ha: a>=2, None),
 "1 + les deux marquent": (lambda M: M[1:,1:][d[1:,1:]>0].sum(), lambda h,a,hh,ha: h>a and a>0, None),
 "2 + les deux marquent": (lambda M: M[1:,1:][d[1:,1:]<0].sum(), lambda h,a,hh,ha: a>h and h>0, None),
 "1 + plus de 2,5": (lambda M: M[(d>0)&(t>2)].sum(), lambda h,a,hh,ha: h>a and h+a>2, None),
 "2 + plus de 2,5": (lambda M: M[(d<0)&(t>2)].sum(), lambda h,a,hh,ha: a>h and h+a>2, None),
 "BTTS + plus de 2,5": (lambda M: M[1:,1:][t[1:,1:]>2].sum(), lambda h,a,hh,ha: h>0 and a>0 and h+a>2, None),
 "Domicile gagne sans encaisser": (lambda M: M[1:,0].sum(), lambda h,a,hh,ha: h>0 and a==0, None),
 "Extérieur gagne sans encaisser": (lambda M: M[0,1:].sum(), lambda h,a,hh,ha: a>0 and h==0, None),
 "Domicile par 1 but": (lambda M: M[d==1].sum(), lambda h,a,hh,ha: h-a==1, None),
 "Domicile par 2+": (lambda M: M[d>=2].sum(), lambda h,a,hh,ha: h-a>=2, None),
 "0-1 but": (lambda M: M[t<=1].sum(), lambda h,a,hh,ha: h+a<=1, None),
 "2-3 buts": (lambda M: M[(t>=2)&(t<=3)].sum(), lambda h,a,hh,ha: 2<=h+a<=3, None),
 "Impair": (lambda M: M[t%2==1].sum(), lambda h,a,hh,ha: (h+a)%2==1, None),
}
def ht_probs(lh, la):
    A = np.outer(pois(lh*SH), pois(la*SH)); B = np.outer(pois(lh*(1-SH)), pois(la*(1-SH)))   # mi-temps 1 et 2 indépendantes
    return A/A.sum(), B/B.sum()
HTMK = {
 "MT : domicile mène": (lambda A,B: A[d>0].sum(), lambda h,a,hh,ha: hh>ha),
 "MT : nul": (lambda A,B: A[d==0].sum(), lambda h,a,hh,ha: hh==ha),
 "MT/FT 1/1": (None, lambda h,a,hh,ha: hh>ha and h>a),
 "MT/FT N/1": (None, lambda h,a,hh,ha: hh==ha and h>a),
 "MT/FT N/N": (None, lambda h,a,hh,ha: hh==ha and h==a),
 "But dans les 2 mi-temps": (lambda A,B: (1-A[0,0])*(1-B[0,0]), lambda h,a,hh,ha: hh+ha>0 and (h+a)-(hh+ha)>0),
 "MT : moins de 1,5": (lambda A,B: A[t<=1].sum(), lambda h,a,hh,ha: hh+ha<=1),
}
def htft(A, B, f):
    s = 0.0
    for i in range(G+1):
        for j in range(G+1):
            if A[i,j] < 1e-9: continue
            s += A[i,j] * sum(B[k,l] for k in range(G+1) for l in range(G+1) if f(i+k, j+l, i, j))
    return s
rows = {k: [] for k in list(MK) + list(HTMK)}
for r in D.itertuples():
    M = ft(r.lh, r.la); A, B = ht_probs(r.lh, r.la); h, a, hh, ha = r.FTHG, r.FTAG, int(r.HTHG), int(r.HTAG)
    for k, (fp, fw, valid) in MK.items():
        if valid and not valid(h, a): continue
        rows[k].append((fp(M), fw(h,a,hh,ha)))
    for k, (fp, fw) in HTMK.items():
        p = fp(A, B) if fp else htft(A, B, fw)
        rows[k].append((p, fw(h,a,hh,ha)))
print(f"{'pari':32s} {'annoncé':>8s} {'réalisé':>8s} {'écart':>6s}   calibration par tranche (annoncé→réalisé)")
for k, v in rows.items():
    p = np.array([x[0] for x in v]); y = np.array([x[1] for x in v], float)
    bins = []
    for lo, hi in ((0,.3),(.3,.5),(.5,.7),(.7,1.01)):
        m = (p >= lo) & (p < hi)
        if m.sum() >= 150: bins.append(f"{p[m].mean()*100:.0f}→{y[m].mean()*100:.0f}")
    print(f"{k:32s} {p.mean()*100:7.1f}% {y.mean()*100:7.1f}% {(y.mean()-p.mean())*100:+5.1f}   {'  '.join(bins)}")
