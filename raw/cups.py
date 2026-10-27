"""Coupes nationales des 5 grands pays (voir UPDATE.md, étape « Coupes nationales »).

Un fichier raw/cup_<clé>.txt par coupe, heures de Paris (#tz=paris) :
  D Mon YYYY|HH:MM|Domicile|Extérieur|score|n
  - score : score à la fin du temps réglementaire (90 minutes, prolongation et tirs au but NON comptés : c'est ce qui
    règle les paris 1N2), « 1-1 » ou « 1-1 (0-1) » avec la mi-temps ; vide si non joué ;
  - n : « n » si le match se joue sur terrain neutre (finale, demi-finales de FA Cup…), sinon rien.
Seuls les matchs entre deux équipes suivies par l'application sont saisis (5 grands championnats et divisions
inférieures suivies) ; les matchs contre un club non suivi (3e division, amateurs…) sont ignorés.
Noms : exactement ceux des championnats (raw/<championnat>.txt pour les 5 grands, fd/ pour les autres).
"""
# clé : (nom affiché, pays, championnats où chercher les équipes, du plus haut au plus bas)
CUPS = {
    "cdf": ("Coupe de France", "France", ["l1", "l2"]),
    "fac": ("FA Cup", "Angleterre", ["pl", "champ", "eng3", "eng4"]),
    "efl": ("Coupe de la Ligue anglaise", "Angleterre", ["pl", "champ", "eng3", "eng4"]),
    "cdr": ("Copa del Rey", "Espagne", ["liga", "liga2"]),
    "cit": ("Coppa Italia", "Italie", ["sa", "sb"]),
    "dfb": ("Coupe d'Allemagne", "Allemagne", ["bl", "bl2"]),
}
# Cotes relevées à la main (facultatif) : {"dfb": {("Domicile","Extérieur"): {"1x2": ("Bookmaker", [c1, cN, c2])}}}
# ODDS_AT : date du relevé (AAAA-MM-JJ). Effacer les cotes des matchs joués.
ODDS_AT = "2026-10-27"
ODDS = {
    "efl": {   # bet365, d'après olbg.com (article du 4e tour)
        ("Bradford", "Peterboro"): {"1x2": ("bet365", [1.67, 3.75, 5.00])},
        ("Fleetwood Town", "Arsenal"): {"1x2": ("bet365", [17.0, 12.0, 1.08])},
        ("Manchester City", "Brighton & Hove Albion"): {"1x2": ("bet365", [1.62, 4.33, 4.75])},
        ("AFC Bournemouth", "Aston Villa"): {"1x2": ("bet365", [2.25, 3.50, 3.00])},
        ("Fulham", "Crystal Palace"): {"1x2": ("bet365", [1.83, 3.75, 4.00])},
        ("Sunderland", "Brentford"): {"1x2": ("bet365", [3.60, 3.60, 1.95])},
        ("Liverpool", "Chelsea"): {"1x2": ("bet365", [2.45, 3.80, 2.55])},
        ("Everton", "Newcastle United"): {"1x2": ("bet365", [2.25, 3.50, 3.00])},
    },
    "dfb": {
        ("FC Bayern München", "Magdeburg"): {"1x2": ("bet365", [1.04, 15.0, 26.0])},                 # wettfreunde.net
        ("Borussia Dortmund", "Werder Bremen"): {"1x2": ("meilleure cote", [1.42, 5.25, 7.60])},     # wettbasis.com
        ("Borussia Mönchengladbach", "Karlsruhe"): {"1x2": ("meilleure cote", [1.40, 5.75, 8.50])},  # wettbasis.com
    },
}
SOURCES = [
    ["dfb.de — Coupe d'Allemagne, horaires du 2e tour", "https://www.dfb.de/news/das-sind-die-zeitgenauen-ansetzungen-der-zweiten-pokalrunde"],
    ["dave.sport — Coupe de la Ligue anglaise, 4e tour", "https://dave.sport/news/carabao-cup-fixtures-tv/"],
    ["OLBG — cotes bet365 du 4e tour de la Coupe de la Ligue anglaise (relevé du 27/10)", "https://www.olbg.com/news/carabao-cup-fourth-round-odds-betting-sites-can-barely-separate-liverpool-and-chelsea-carabao-cup-fourth-round"],
]
