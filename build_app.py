"""Inject data.json into app.html.

  python3 build_app.py <remote_data_url>   -> dist/index.html (APK / standalone, fetches updates from the URL)
  python3 build_app.py                      -> dist/index.html without online updates
  EDITION=pub python3 build_app.py <url>    -> version publique (sans Metabet, sans clé de cotes, porte 18 ans et plus)
"""
import os, sys, pathlib
ROOT = pathlib.Path(__file__).parent
remote = sys.argv[1] if len(sys.argv) > 1 else ""
html = (ROOT / "app.html").read_text(encoding="utf-8")
data = (ROOT / "data.json").read_text(encoding="utf-8").replace("</", "<\\/")
assert "/*DATA*/null" in html and '"/*REMOTE*/"' in html
html = html.replace("/*DATA*/null", data, 1)
build = os.environ.get("VERSION_CODE", "0")
assert "/*BUILD*/0" in html
html = html.replace("/*BUILD*/0", str(int(build)), 1)
edition = os.environ.get("EDITION", "perso")
assert edition in ("perso", "pub") and '"/*EDITION*/perso"' in html
html = html.replace('"/*EDITION*/perso"', '"' + edition + '"', 1)
if remote:
    html = html.replace('"/*REMOTE*/"', '"' + remote + '"', 1)
# Version web (iPhone, ordinateur) : document complet + icône d'écran d'accueil (EDITION=pub WEB=1)
if os.environ.get("WEB") == "1":
    head = ('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
            '<meta name="apple-mobile-web-app-title" content="Prono Lab">\n'
            '<link rel="apple-touch-icon" href="icon-180.png">\n<link rel="icon" type="image/png" href="icon-192.png">\n'
            '<link rel="manifest" href="manifest.json">\n')
    html = head + html
out = ROOT / "dist"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(html, encoding="utf-8")
print("dist/index.html", len(html), "octets", "· édition", edition, "· mise à jour depuis", remote or "(aucune)")
