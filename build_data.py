"""Assemble data.json for Prono Lab from raw/*.txt (results + fixtures) and raw/meta.py.

Raw line format: "D Mon YYYY|HH:MM|Home|Away|score"  (time = UK local, Paris = UK + 1h; empty score = not played;
score "2-1" or "2-1 (1-0)" with the half-time score in brackets when the source gives it)
"""
import json, sys, csv, datetime as dt, importlib.util, pathlib

ROOT = pathlib.Path(__file__).parent
def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "raw" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
meta = _load("meta")
euro = _load("euro")
context = _load("context")

def parse(lg):
    out, shift = [], 1          # par défaut : heure du Royaume-Uni (+1 h pour Paris)
    for ln in (ROOT / "raw" / f"{lg}.txt").read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        if ln.startswith("#"):
            if "tz=paris" in ln: shift = 0
            continue
        d, t, h, a, s = (ln.split("|") + [""])[:5]
        when = dt.datetime.strptime(f"{d.strip()} {t.strip()}", "%d %b %Y %H:%M") + dt.timedelta(hours=shift)
        m = {"d": when.strftime("%Y-%m-%dT%H:%M"), "h": h.strip(), "a": a.strip()}
        s = s.strip().replace("–", "-")
        if s:
            # score final, suivi éventuellement du score à la mi-temps entre parenthèses : « 2-1 (1-0) »
            ft, _, ht = s.partition("(")
            hs, as_ = ft.strip().split("-")
            m["s"] = [int(hs), int(as_)]
            if ht.strip():
                hh, ha = ht.strip(" )").split("-")
                m["ht"] = [int(hh), int(ha)]
                assert m["ht"][0] <= m["s"][0] and m["ht"][1] <= m["s"][1], f"{lg}: score mi-temps incohérent {ln}"
        out.append(m)
    out.sort(key=lambda m: m["d"])
    return out

def attach_odds(lg, matches, odds, odds_at):
    for (h, a), spec in odds.items():
        hit = [m for m in matches if m["h"] == h and m["a"] == a and "s" not in m]
        if not hit:
            print(f"  ! {lg}: cote ignorée (match joué ou absent) {h}-{a}")
            continue
        # spec = (bookmaker, [1, N, 2])  ou  {"1x2": (bk, [1,N,2]), "ou": (bk, [plus 2,5, moins 2,5]), "btts": (bk, [oui, non])}
        if isinstance(spec, tuple):
            spec = {"1x2": spec}
        od = {"at": odds_at}
        if "1x2" in spec:
            od["bk"], od["o"] = spec["1x2"][0], list(spec["1x2"][1]); assert len(od["o"]) == 3
        for key in ("ou", "btts"):
            if key in spec:
                bk, o = spec[key]; assert len(o) == 2
                od[key] = {"bk": bk, "o": list(o)}
        assert all(x > 1 for x in od.get("o", []) + sum((od[k]["o"] for k in ("ou", "btts") if k in od), []))
        hit[0]["odds"] = od

def attach_context(lg, matches):
    for (h, a), c in context.CONTEXT.get(lg, {}).items():
        hit = [m for m in matches if m["h"] == h and m["a"] == a and "s" not in m]
        if not hit:
            print(f"  ! {lg}: contexte ignoré (match joué ou absent) {h}-{a}")
            continue
        assert c.get("lvl") in ("alerte", "info") and c.get("why") and str(c.get("src", "")).startswith("http"), f"contexte incomplet {lg} {h}-{a}"
        hit[0]["ctx"] = {"lvl": c["lvl"], "why": c["why"], "src": c["src"], "at": context.CHECKED_AT}

# ---------- Autres championnats européens : football-data.co.uk (fd/), mis à jour chaque jour par une tâche GitHub ----------
FD = {  # code: (clé, nom affiché, pays)
    "E1": ("champ", "Championship", "Angleterre"), "E2": ("eng3", "League One", "Angleterre"), "E3": ("eng4", "League Two", "Angleterre"),
    "SC0": ("sco", "Premiership écossaise", "Écosse"), "SC1": ("sco2", "Championship écossais", "Écosse"),
    "D2": ("bl2", "2. Bundesliga", "Allemagne"), "I2": ("sb", "Serie B", "Italie"), "SP2": ("liga2", "LaLiga 2", "Espagne"),
    "F2": ("l2", "Ligue 2", "France"), "N1": ("ere", "Eredivisie", "Pays-Bas"), "B1": ("bel", "Pro League", "Belgique"),
    "P1": ("por", "Liga Portugal", "Portugal"), "T1": ("tur", "Süper Lig", "Turquie"), "G1": ("gre", "Super League", "Grèce"),
}
FD_SEASON, FD_PREV = "2627", "2526"
def _rows(path):
    if not path.exists(): return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("HomeTeam") and r.get("AwayTeam")]
def _fd_when(r):
    # heure du Royaume-Uni → Paris (+1 h toute l'année : les deux pays changent d'heure le même jour)
    t = (r.get("Time") or "15:00").strip() or "15:00"
    return (dt.datetime.strptime(r["Date"].strip(), "%d/%m/%Y") + dt.timedelta(hours=int(t[:2]) + 1, minutes=int(t[3:5]))).strftime("%Y-%m-%dT%H:%M")
def _num(x):
    try: return float(x)
    except (TypeError, ValueError): return None
def fixtures_at(now_paris):
    """Date (AAAA-MM-JJ) à laquelle le contenu actuel de fd/fixtures.csv a été vu pour la première fois.
    Les cotes de ce fichier datent de sa publication, pas de la reconstruction de data.json : l'empreinte
    fd/fixtures.stamp.json garde la date tant que le fichier ne change pas (règle des 72 h de l'application)."""
    import hashlib
    f, st = ROOT / "fd" / "fixtures.csv", ROOT / "fd" / "fixtures.stamp.json"
    if not f.exists(): return None
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    prev = json.loads(st.read_text(encoding="utf-8")) if st.exists() else {}
    if prev.get("sha256") == sha and prev.get("at"):
        return prev["at"][:10]
    st.write_text(json.dumps({"sha256": sha, "at": now_paris}, ensure_ascii=False) + "\n", encoding="utf-8")
    return now_paris[:10]

# Cotes des 5 grands championnats tirées du même fixtures.csv (codes football-data → clés et noms statz.ai)
FD_BIG = {"E0": "pl", "F1": "l1", "SP1": "liga", "I1": "sa", "D1": "bl"}
FD_ALIAS = {   # nom football-data → nom statz.ai (les noms identiques n'ont pas besoin d'y figurer)
    "pl": {"Bournemouth": "AFC Bournemouth", "Brighton": "Brighton & Hove Albion", "Coventry": "Coventry City", "Hull": "Hull City",
           "Ipswich": "Ipswich Town", "Leeds": "Leeds United", "Man City": "Manchester City", "Man United": "Manchester United",
           "Newcastle": "Newcastle United", "Nott'm Forest": "Nottingham Forest", "Tottenham": "Tottenham Hotspur"},
    "l1": {"Angers": "Angers SCO", "Lille": "LOSC Lille", "Lyon": "Olympique Lyonnais", "Marseille": "Olympique Marseille",
           "Paris FC": "Paris", "Paris SG": "Paris Saint Germain"},
    "liga": {"Alaves": "Deportivo Alavés", "Ath Bilbao": "Athletic Club", "Ath Madrid": "Atlético Madrid", "Barcelona": "FC Barcelona",
             "Betis": "Real Betis", "Celta": "Celta de Vigo", "Espanol": "Espanyol", "La Coruna": "Deportivo La Coruña", "Malaga": "Málaga",
             "Santander": "Racing Santander", "Sociedad": "Real Sociedad", "Vallecano": "Rayo Vallecano"},
    "sa": {"Milan": "AC Milan"},
    "bl": {"Augsburg": "FC Augsburg", "Bayern Munich": "FC Bayern München", "Dortmund": "Borussia Dortmund", "Ein Frankfurt": "Eintracht Frankfurt",
           "FC Koln": "FC Köln", "Freiburg": "SC Freiburg", "Hamburg": "Hamburger SV", "Hoffenheim": "TSG Hoffenheim",
           "Leverkusen": "Bayer 04 Leverkusen", "M'gladbach": "Borussia Mönchengladbach", "Mainz": "FSV Mainz 05",
           "Stuttgart": "VfB Stuttgart", "Union Berlin": "FC Union Berlin"},
}
def _fd_odds(r, at):
    o = [_num(r.get(c)) for c in ("AvgH", "AvgD", "AvgA")]
    if not all(x and x > 1 for x in o): return None
    od = {"at": at, "bk": "moyenne des bookmakers", "o": o, "src": "fd"}
    ou = [_num(r.get("Avg>2.5")), _num(r.get("Avg<2.5"))]
    if all(x and x > 1 for x in ou): od["ou"] = {"bk": "moyenne des bookmakers", "o": ou}
    return od

def attach_fd_big(data, at):
    """Cotes football-data pour les 5 grands championnats : remplacent le relevé manuel (raw/meta.py) quand elles sont
    au moins aussi récentes ; à date égale, le relevé manuel (meilleure cote, parfois « les deux marquent ») est gardé."""
    if not at: return
    n = 0
    for r in _rows(ROOT / "fd" / "fixtures.csv"):
        lg = FD_BIG.get(r.get("Div", "").strip())
        if not lg or lg not in data["leagues"]: continue
        L = data["leagues"][lg]; alias = FD_ALIAS.get(lg, {})
        h, a = (alias.get(x.strip(), x.strip()) for x in (r["HomeTeam"], r["AwayTeam"]))
        ids = {t["id"] for t in L["teams"]}
        if h not in ids or a not in ids:
            print(f"  ! {lg}: équipe football-data inconnue {r['HomeTeam']}-{r['AwayTeam']} (ajouter à FD_ALIAS)"); continue
        hit = [m for m in L["matches"] if m["h"] == h and m["a"] == a and "s" not in m]
        if not hit: continue                                  # déjà joué, ou pas encore dans raw/
        m = hit[0]
        if _fd_when(r)[:10] != m["d"][:10]:
            print(f"  ! {lg}: date différente pour {h}-{a} : raw {m['d']} / football-data {_fd_when(r)} (vérifier le calendrier)")
        od = _fd_odds(r, at)
        if not od: continue
        if "odds" in m and m["odds"].get("at", "") > at: continue
        if "odds" in m and m["odds"].get("at", "") == at and m["odds"].get("src") != "fd": continue
        m["odds"] = od; n += 1
    print(f"cotes football-data des 5 grands championnats : {n} match(s), relevé du {at}")

def load_fd(data, odds_at):
    root = ROOT / "fd"
    if not root.exists(): return
    fixtures = _rows(root / "fixtures.csv")
    for code, (key, name, country) in FD.items():
        cur, prev = _rows(root / f"{code}_{FD_SEASON}.csv"), _rows(root / f"{code}_{FD_PREV}.csv")
        if not cur: continue
        matches, seen = [], set()
        for r in cur:
            if r.get("FTHG", "") == "" or r.get("FTAG", "") == "": continue
            m = {"d": _fd_when(r), "h": r["HomeTeam"].strip(), "a": r["AwayTeam"].strip(), "s": [int(float(r["FTHG"])), int(float(r["FTAG"]))]}
            if r.get("HTHG", "") != "" and r.get("HTAG", "") != "": m["ht"] = [int(float(r["HTHG"])), int(float(r["HTAG"]))]
            matches.append(m); seen.add((m["h"], m["a"]))
        for r in fixtures:
            if r.get("Div", "").strip() != code: continue
            h, a = r["HomeTeam"].strip(), r["AwayTeam"].strip()
            if (h, a) in seen: continue           # déjà joué et dans les résultats
            m = {"d": _fd_when(r), "h": h, "a": a}
            od = _fd_odds(r, odds_at)
            if od: m["odds"] = od
            matches.append(m); seen.add((h, a))
        matches.sort(key=lambda m: m["d"])
        names = sorted({m["h"] for m in matches} | {m["a"] for m in matches})
        tot = {}
        for r in prev:
            if r.get("FTHG", "") == "": continue
            for t, f, a in ((r["HomeTeam"].strip(), r["FTHG"], r["FTAG"]), (r["AwayTeam"].strip(), r["FTAG"], r["FTHG"])):
                x = tot.setdefault(t, [0, 0, 0]); x[0] += 1; x[1] += int(float(f)); x[2] += int(float(a))
        pg, pgf = sum(v[0] for v in tot.values()), sum(v[1] for v in tot.values())
        data["leagues"][key] = {"name": name, "country": country, "xgAsOf": None, "source": "fd",
            "priorMu": round(pgf / pg, 4) if pg else 1.3,
            "teams": [{"id": n, "name": n, "xg": {"p": 0, "f": 0, "a": 0},
                       "prior": ({"p": tot[n][0], "f": tot[n][1], "a": tot[n][2]} if n in tot else None)} for n in names],
            "matches": matches}
    data["sources"] = data["sources"] + [["football-data.co.uk (autres championnats, et cotes moyennes des 5 grands championnats quand elles sont plus récentes)", "https://www.football-data.co.uk/data.php"]]

def build(generated_at, odds_at):
    data = {"generatedAt": generated_at, "version": 2, "sources": meta.SOURCES, "leagues": {}, "contextAt": context.CHECKED_AT,
            "oddsManualAt": odds_at}   # date du relevé manuel (raw/meta.py, raw/euro.py), reprise telle quelle par --auto
    for lg, L in meta.LEAGUES.items():
        matches = parse(lg)
        names = sorted({m["h"] for m in matches} | {m["a"] for m in matches})
        missing = [n for n in names if n not in L["xg"] or n not in L["prior"]]
        if missing:
            sys.exit(f"{lg}: équipes sans xG ou prior: {missing}")
        attach_odds(lg, matches, L["odds"], odds_at)
        attach_context(lg, matches)
        pg, pgf = L["priorTotals"]
        teams = []
        for n in names:
            xp, xf, xa = L["xg"][n]
            pr = L["prior"][n]
            teams.append({"id": n, "name": L["display"].get(n, n),
                          "xg": {"p": xp, "f": xf, "a": xa},
                          "prior": None if pr is None else {"p": pr[0], "f": pr[1], "a": pr[2]}})
        data["leagues"][lg] = {"name": L["name"], "country": L["country"], "xgAsOf": L["xgAsOf"],
                               "priorMu": round(pgf / pg, 4), "teams": teams, "matches": matches}
    # Coupes d'Europe : modèle Elo-like ajusté dans l'application (pays, niveau domestique, coupe, résultats européens)
    data["uefaCountry"] = euro.COUNTRY_COEF
    data["sources"] = meta.SOURCES + euro.SOURCES
    for lg, clubs in euro.CLUBS.items():
        matches = parse(lg)
        names = sorted({m["h"] for m in matches} | {m["a"] for m in matches})
        missing = [n for n in names if n not in clubs]
        if missing:
            sys.exit(f"{lg}: clubs inconnus {missing}")
        for n, (disp, ctry, dom) in clubs.items():
            if ctry not in euro.COUNTRY_COEF: sys.exit(f"{lg}: pays sans coefficient {ctry}")
            if dom and dom[1] not in {t["id"] for t in data["leagues"][dom[0]]["teams"]}:
                sys.exit(f"{lg}: lien domestique introuvable {n} -> {dom}")
        attach_odds(lg, matches, getattr(euro, "ODDS", {}).get(lg, {}), odds_at)
        attach_context(lg, matches)
        data["leagues"][lg] = {"name": euro.NAMES[lg], "type": "euro", "coefAsOf": euro.COEF_AS_OF,
            "teams": [{"id": n, "name": d, "country": c, "dom": ({"lg": dm[0], "id": dm[1]} if dm else None)} for n, (d, c, dm) in clubs.items()],
            "matches": matches}
    fx_at = fixtures_at(generated_at)
    attach_fd_big(data, fx_at)
    load_fd(data, fx_at or generated_at[:10])
    return data

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # reconstruction automatique (tâche GitHub) : heure de Paris maintenant, date des cotes des 5 championnats inchangée
        from zoneinfo import ZoneInfo
        gen = dt.datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%dT%H:%M")
        prev = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
        ats = [m["odds"]["at"] for k, L in prev["leagues"].items() if L.get("source") != "fd" for m in L["matches"] if "odds" in m and m["odds"].get("src") != "fd"]
        odds_at = prev.get("oddsManualAt") or (max(ats) if ats else gen[:10])
    else:
        gen = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now().strftime("%Y-%m-%dT%H:%M")
        odds_at = sys.argv[2] if len(sys.argv) > 2 else gen[:10]
    data = build(gen, odds_at)
    (ROOT / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for lg, L in data["leagues"].items():
        played = [m for m in L["matches"] if "s" in m]
        print(lg, len(L["teams"]), "équipes,", len(played), "joués,", len(L["matches"]) - len(played), "à venir,",
              sum(1 for m in L["matches"] if "odds" in m), "cotes")
