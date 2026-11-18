#!/usr/bin/env python3
"""Compétitions féminines : résultats et calendrier depuis ESPN (site.api.espn.com), un appel par jour et par compétition.

  python3 fetch_espn.py            -> 10 jours passés + 21 jours à venir (rattrapage complet la première fois)
  python3 fetch_espn.py --backfill -> tout depuis le 1er juillet 2025 (saison précédente, pour la force de départ)

Résultat : espn/<clé>.json = liste de matchs {id, utc, h, a, st, s?, ht?} triée par date.
Lancé par .github/workflows/fetch-leagues.yml (le bac à sable de Claude n'a pas accès à ESPN).
"""
import json, sys, time, pathlib, datetime as dt, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "espn"
API = "https://site.api.espn.com/apis/site/v2/sports/soccer"
# clé : (code ESPN, nom affiché, pays) ; pays None = coupe d'Europe
WOMEN = {
    "fw":   ("fra.w.1",         "Première Ligue (F)",       "FRA"),
    "ew":   ("eng.w.1",         "WSL (F)",                  "ENG"),
    "sw":   ("esp.w.1",         "Liga F (F)",               "ESP"),
    "nw":   ("ned.w.1",         "Eredivisie (F)",           "NED"),
    "uwcl": ("uefa.wchampions", "Ligue des champions (F)",  None),
    "uwec": ("uefa.w.europa",   "Europa Cup (F)",           None),
}
BACKFILL_FROM = dt.date(2025, 7, 1)
DONE = {"STATUS_FULL_TIME", "STATUS_FINAL", "STATUS_FINAL_AET", "STATUS_FINAL_PEN", "STATUS_END_OF_EXTRATIME"}
DROP = {"STATUS_POSTPONED", "STATUS_CANCELED", "STATUS_ABANDONED", "STATUS_FORFEIT"}

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (prono-lab)", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1: print(f"  ! {url}: {e}"); return None
            time.sleep(1.5 * (i + 1))

def day(code, d):
    js = get(f"{API}/{code}/scoreboard?dates={d:%Y%m%d}")
    if js is None: return None
    out = []
    for e in js.get("events", []):
        c = e["competitions"][0]; st = e["status"]["type"]["name"]
        if st in DROP: continue
        side = {x["homeAway"]: x for x in c["competitors"]}
        if "home" not in side or "away" not in side: continue
        m = {"id": e["id"], "utc": e["date"], "h": side["home"]["team"]["displayName"], "a": side["away"]["team"]["displayName"], "st": st}
        if st in DONE:
            try:
                m["s"] = [int(side["home"]["score"]), int(side["away"]["score"])]
                lh, la = side["home"].get("linescores") or [], side["away"].get("linescores") or []
                if lh and la: m["ht"] = [int(lh[0]["value"]), int(la[0]["value"])]
            except (KeyError, ValueError, TypeError): m.pop("s", None)
        out.append(m)
    return out

def main():
    OUT.mkdir(exist_ok=True)
    today = dt.datetime.now(dt.timezone.utc).date()
    full = "--backfill" in sys.argv
    for key, (code, name, _) in WOMEN.items():
        f = OUT / f"{key}.json"
        have = {m["id"]: m for m in json.loads(f.read_text())} if f.exists() else {}
        start = BACKFILL_FROM if (full or not have) else today - dt.timedelta(days=10)
        days = [start + dt.timedelta(days=i) for i in range((today + dt.timedelta(days=21) - start).days + 1)]
        with ThreadPoolExecutor(8) as ex:
            res = list(ex.map(lambda d: (d, day(code, d)), days))
        fail = sum(1 for _, r in res if r is None)
        if fail == len(days):
            print(f"{key}: ESPN injoignable, fichier conservé"); continue
        # les jours relus remplacent ce qu'on avait pour ces jours (matchs reportés ou déplacés)
        got = {d.isoformat() for d, r in res if r is not None}
        have = {i: m for i, m in have.items() if m["utc"][:10] not in got}
        for _, r in res:
            for m in r or []: have[m["id"]] = m
        ms = sorted(have.values(), key=lambda m: (m["utc"], m["h"]))
        f.write_text(json.dumps(ms, ensure_ascii=False, indent=0))
        print(f"{key} ({name}) : {len(ms)} matchs, {sum(1 for m in ms if 's' in m)} joués, {len(days)} jours lus, {fail} échecs")

if __name__ == "__main__":
    main()
