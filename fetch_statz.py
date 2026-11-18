#!/usr/bin/env python3
"""5 grands championnats et Ligue des champions : résultats, calendrier et xG lus sur statz.ai, automatiquement.

Lancé par .github/workflows/fetch-leagues.yml (deux fois par jour). Le bac à sable de Claude n'a plus accès à statz.ai
depuis mi-novembre 2026 : la lecture se fait donc depuis GitHub.

- raw/<lg>.txt : les scores des matchs joués sont ajoutés (le score à la mi-temps déjà saisi est gardé), les matchs à venir
  des 12 prochains jours (16 pour la Ligue des champions) sont ajoutés ou mis à l'heure ; un match à venir qui a disparu
  du calendrier (report sans date) est retiré. Heures du Royaume-Uni, comme sur statz.ai.
- raw/xg_auto.json : xG pour et contre de chaque équipe (« xG 22.8, xGA 11.5 … from 10 matches »), repris par
  build_data.py à la place de raw/meta.py quand il est plus récent.
"""
import json, re, time, pathlib, datetime as dt, urllib.request, html

ROOT = pathlib.Path(__file__).resolve().parent
SLUGS = {"l1": "ligue-1", "pl": "premier-league", "liga": "la-liga", "sa": "serie-a", "bl": "bundesliga", "ucl": "champions-league"}
AHEAD = {"ucl": 16}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
ROW = re.compile(r'<tr><td>([^<]*)</td><td>([^<]*)</td><td><a href="/h2h/[^"]*">([^<]*)</a></td><td>([^<]*)</td></tr>')

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")

def day(s):   # « 21st Aug 2026 » -> « 21 Aug 2026 »
    return re.sub(r"^(\d+)(st|nd|rd|th)\b", r"\1", s.strip())

def fixtures(lg):
    rows = []
    for d, t, teams, sc in ROW.findall(get(f"https://statz.ai/competitions/{SLUGS[lg]}/fixtures")):
        teams = html.unescape(teams)
        if " vs " not in teams: continue
        h, a = teams.split(" vs ", 1)
        sc = sc.strip()
        rows.append({"d": day(d), "t": t.strip(), "h": h.strip(), "a": a.strip(), "s": sc if re.fullmatch(r"\d+-\d+", sc) else ""})
    return rows

def update_file(lg, rows, today):
    f = ROOT / "raw" / f"{lg}.txt"
    lines = f.read_text(encoding="utf-8").splitlines() if f.exists() else []
    head = [ln for ln in lines if ln.startswith("#")]
    old = {}
    for ln in lines:
        if not ln.strip() or ln.startswith("#"): continue
        p = (ln.split("|") + ["", ""])[:6]
        old[(p[2].strip(), p[3].strip())] = p
    when = lambda r: dt.datetime.strptime(f"{r['d']} {r['t']}", "%d %b %Y %H:%M")
    limit = today + dt.timedelta(days=AHEAD.get(lg, 12))
    out, seen, added, scored, moved, fixed = [], set(), 0, 0, 0, []
    for r in rows:
        k = (r["h"], r["a"]); seen.add(k)
        o = old.get(k)
        if r["s"]:
            s = r["s"]
            if o and o[4].split("(")[0].strip() == s and "(" in o[4]: s = o[4].strip()   # garder la mi-temps déjà saisie
            if not o or not o[4].strip(): scored += 1
            elif o[4].split("(")[0].strip() != s.split("(")[0].strip(): fixed.append(f"{r['h']}-{r['a']} {o[4].strip()} -> {s}")
            out.append([r["d"], r["t"], r["h"], r["a"], s] + ([o[5]] if o and o[5].strip() else []))
        elif when(r) <= limit and when(r) >= today - dt.timedelta(days=2):
            if not o: added += 1
            elif (o[0].strip(), o[1].strip()) != (r["d"], r["t"]): moved += 1
            out.append([r["d"], r["t"], r["h"], r["a"], ""] + ([o[5]] if o and o[5].strip() else []))
    # matchs joués saisis à la main mais absents de statz (barrages, etc.) : gardés
    for k, p in old.items():
        if k not in seen and p[4].strip(): out.append(p[:5] + ([p[5]] if p[5].strip() else []))
    out.sort(key=lambda p: (dt.datetime.strptime(f"{p[0]} {p[1]}", "%d %b %Y %H:%M"), p[2]))
    text = "\n".join(head + ["|".join(p) for p in out]) + "\n"
    if text != ("\n".join(lines) + "\n"):
        f.write_text(text, encoding="utf-8")
    for x in fixed: print(f"  score corrigé ({lg}) : {x}")
    return scored, added, moved, len(out)

def xg(lg):
    for attempt in range(3):
        page = get(f"https://statz.ai/competitions/{SLUGS[lg]}/xg")
        t = _xg_table(page)
        if t: return t
        print(f"  {lg} xG : essai {attempt + 1} sans tableau ({len(page)} caractères, ItemList={page.count('ItemList')}, xG={page.count('xG')}) : {page[:120]!r}")
        time.sleep(5)
    return None

def _xg_table(page):
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        try: d = json.loads(blob)
        except ValueError: continue
        if isinstance(d, dict) and d.get("@type") == "ItemList" and "xG" in d.get("name", ""):
            teams = {}
            for it in d.get("itemListElement", []):
                m = re.search(r"xG ([\d.]+), xGA ([\d.]+).*?from (\d+) match", it.get("description", ""))
                if m: teams[html.unescape(it["name"])] = [int(m.group(3)), float(m.group(1)), float(m.group(2))]
            return teams
    return None

def main():
    today = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    ok = True
    xa_path = ROOT / "raw" / "xg_auto.json"
    xa = json.loads(xa_path.read_text(encoding="utf-8")) if xa_path.exists() else {}
    for lg in SLUGS:
        try:
            rows = fixtures(lg)
            if len(rows) < 50: raise ValueError(f"seulement {len(rows)} lignes lues (page modifiée ?)")
            sc, ad, mv, n = update_file(lg, rows, today)
            print(f"{lg}: {len(rows)} matchs lus, {sc} score(s) ajouté(s), {ad} match(s) ajouté(s), {mv} déplacé(s), {n} lignes")
        except Exception as e:
            ok = False; print(f"::warning::{lg} calendrier : {e}")
        if lg == "ucl": continue
        try:
            t = xg(lg)
            if not t or len(t) < 16: raise ValueError("tableau xG introuvable")
            if xa.get(lg, {}).get("teams") != t:
                xa[lg] = {"asOf": dt.datetime.now().strftime("%Y-%m-%d"), "teams": t}
            print(f"{lg}: xG de {len(t)} équipes")
        except Exception as e:
            ok = False; print(f"::warning::{lg} xG : {e}")
    xa_path.write_text(json.dumps(xa, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    # une page en panne ne bloque pas le reste de la mise à jour (avertissement dans le journal de la tâche)

if __name__ == "__main__":
    main()
