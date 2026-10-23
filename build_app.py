"""Inject data.json into app.html.

  python3 build_app.py <remote_data_url>   -> dist/index.html (APK / standalone, fetches updates from the URL)
  python3 build_app.py                      -> dist/index.html without online updates
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).parent
remote = sys.argv[1] if len(sys.argv) > 1 else ""
html = (ROOT / "app.html").read_text(encoding="utf-8")
data = (ROOT / "data.json").read_text(encoding="utf-8").replace("</", "<\\/")
assert "/*DATA*/null" in html and '"/*REMOTE*/"' in html
html = html.replace("/*DATA*/null", data, 1)
if remote:
    html = html.replace('"/*REMOTE*/"', '"' + remote + '"', 1)
out = ROOT / "dist"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(html, encoding="utf-8")
print("dist/index.html", len(html), "octets", "· mise à jour depuis", remote or "(aucune)")
