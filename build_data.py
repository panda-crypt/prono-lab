"""Assemble data.json for Prono Lab from raw/*.txt (results + fixtures) and raw/meta.py.

Raw line format: "D Mon YYYY|HH:MM|Home|Away|score"  (time = UK local, Paris = UK + 1h; empty score = not played)
"""
import json, sys, datetime as dt, importlib.util, pathlib

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
        s = s.strip()
        if s:
            hs, as_ = s.replace("–", "-").split("-")
            m["s"] = [int(hs), int(as_)]
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

def build(generated_at, odds_at):
    data = {"generatedAt": generated_at, "version": 2, "sources": meta.SOURCES, "leagues": {}, "contextAt": context.CHECKED_AT}
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
    return data

if __name__ == "__main__":
    gen = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now().strftime("%Y-%m-%dT%H:%M")
    odds_at = sys.argv[2] if len(sys.argv) > 2 else gen[:10]
    data = build(gen, odds_at)
    (ROOT / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for lg, L in data["leagues"].items():
        played = [m for m in L["matches"] if "s" in m]
        print(lg, len(L["teams"]), "équipes,", len(played), "joués,", len(L["matches"]) - len(played), "à venir,",
              sum(1 for m in L["matches"] if "odds" in m), "cotes")
