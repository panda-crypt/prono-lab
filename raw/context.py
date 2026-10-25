"""Contexte des prochains matchs : absences importantes, équipes remaniées, matchs sans enjeu.

Rempli à chaque mise à jour (voir UPDATE.md, étape « Contexte »). Ne jamais inventer : chaque entrée cite sa source.
Clés : noms des équipes exactement comme dans raw/<championnat>.txt.
  lvl = "alerte" : le pronostic du modèle est faussé (ex. buteur et meneur du favori forfaits, équipe B alignée) ;
                   le match est retiré des paris verts, des tickets et des jackpots.
  lvl = "info"   : à savoir, sans effet sur les propositions (ex. un titulaire incertain).
"""
CHECKED_AT = "2026-10-25T09:30"   # date et heure de Paris de la dernière vérification
CONTEXT = {
    # exemple : "l1": {("Paris Saint Germain", "Olympique Lyonnais"): {"lvl": "alerte", "why": "…", "src": "https://…"}},
    "l1": {
        ("Paris Saint Germain", "Olympique Lyonnais"): {"lvl": "alerte",
            "why": "PSG sans Dembélé, Kvaratskhelia, Marquinhos et Nuno Mendes (blessés). Lyon sans Openda, Tagliafico, Ouédraogo (blessés) ni Nakamura (suspendu). Match lundi 26/10 à 20h30.",
            "src": "https://www.ruedesjoueurs.com/pronostic/psg-lyon-5802972.html"},
    },
    "pl": {
        ("Manchester United", "AFC Bournemouth"): {"lvl": "alerte",
            "why": "United sans Sesko, Mainoo, Shaw, Dorgu et Ugarte ; Lisandro Martínez et Rashford incertains.",
            "src": "https://www.premierinjuries.com/injury-table.php"},
        ("Liverpool", "Brighton & Hove Albion"): {"lvl": "info",
            "why": "Liverpool sans Szoboszlai, Frimpong, Ekitike et Bradley ; Isak et Wirtz attendus titulaires. Brighton sans Mitoma.",
            "src": "https://www.football365.com/match-preview/liverpool-v-brighton-prediction-preview"},
    },
    "liga": {
        ("FC Barcelona", "Real Madrid"): {"lvl": "info",
            "why": "Real Madrid sans Vinícius (suspendu), Mendy, Asencio et Rodrygo. Barça sans Olmo, Christensen et Eric García ; Koundé incertain.",
            "src": "https://www.si.com/soccer/real-madrid-injuries-every-player-unavailable-vs-barcelona-10-25-26"},
    },
    "sa": {
        ("Udinese", "AC Milan"): {"lvl": "info",
            "why": "Milan sans Rabiot, Gila et Diego Moreira (blessés).",
            "src": "https://www.lapresse.it/calcio/2026/10/25/inter-fiorentina-oggi-in-serie-a-in-campo-anche-juventus-e-milan-orario-probabili-formazioni-e-dove-vederla-in-tv/"},
    },
    "bl": {
        ("SC Freiburg", "FC Bayern München"): {"lvl": "alerte",
            "why": "Bayern sans Luis Díaz (déchirure musculaire) ni Musiala (reprise) ; Neuer et Pavlović incertains.",
            "src": "https://www.ligainsider.de/bundesliga/verletzte-und-gesperrte-spieler/"},
        ("TSG Hoffenheim", "Bayer 04 Leverkusen"): {"lvl": "info",
            "why": "Leverkusen sans Terrier, Kofane, Ben Seghir et Guéla Doué.",
            "src": "https://www.ligainsider.de/bundesliga/verletzte-und-gesperrte-spieler/"},
    },
}
