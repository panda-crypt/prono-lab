"""Assemble data.json for Prono Lab from raw/*.txt (results + fixtures) and raw/meta.py.

Raw line format: "D Mon YYYY|HH:MM|Home|Away|score"  (time = UK local, Paris = UK + 1h; empty score = not played)
"""
import json, sys, datetime as dt, importlib.util, pathlib

ROOT = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("meta", ROOT / "raw" / "meta.py")
meta = importlib.util.module_from_spec(spec); spec.loader.exec_module(meta)

def parse(lg):
    out = []
    for ln in (ROOT / "raw" / f"{lg}.txt").read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        d, t, h, a, s = (ln.split("|") + [""])[:5]
        when = dt.datetime.strptime(f"{d.strip()} {t.strip()}", "%d %b %Y %H:%M") + dt.timedelta(hours=1)
        m = {"d": when.strftime("%Y-%m-%dT%H:%M"), "h": h.strip(), "a": a.strip()}
        s = s.strip()
        if s:
            hs, as_ = s.replace("–", "-").split("-")
            m["s"] = [int(hs), int(as_)]
        out.append(m)
    out.sort(key=lambda m: m["d"])
    return out

def build(generated_at, odds_at):
    data = {"generatedAt": generated_at, "version": 2, "sources": meta.SOURCES, "leagues": {}}
    for lg, L in meta.LEAGUES.items():
        matches = parse(lg)
        names = sorted({m["h"] for m in matches} | {m["a"] for m in matches})
        missing = [n for n in names if n not in L["xg"] or n not in L["prior"]]
        if missing:
            sys.exit(f"{lg}: équipes sans xG ou prior: {missing}")
        for (h, a), (bk, o) in L["odds"].items():
            hit = [m for m in matches if m["h"] == h and m["a"] == a and "s" not in m]
            if not hit:
                print(f"  ! {lg}: cote ignorée (match joué ou absent) {h}-{a}")
                continue
            hit[0]["odds"] = {"bk": bk, "o": o, "at": odds_at}
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
