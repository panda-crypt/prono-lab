"""Contexte des prochains matchs : absences importantes, équipes remaniées, matchs sans enjeu.

Rempli à chaque mise à jour (voir UPDATE.md, étape « Contexte »). Ne jamais inventer : chaque entrée cite sa source.
Clés : noms des équipes exactement comme dans raw/<championnat>.txt.
  lvl = "alerte" : le pronostic du modèle est faussé (ex. buteur et meneur du favori forfaits, équipe B alignée) ;
                   le match est retiré des paris verts, des tickets et des jackpots.
  lvl = "info"   : à savoir, sans effet sur les propositions (ex. un titulaire incertain).
"""
CHECKED_AT = "2026-11-25T08:45"   # date et heure de Paris de la dernière vérification
CONTEXT = {
    "l1": {}, "pl": {}, "liga": {}, "sa": {},
    "bl": {
        ("Hamburger SV", "FC Bayern München"): {"lvl": "alerte",
            "why": "Bayern : Kane forfait (cheville, plusieurs mois), Neuer et Davies annoncés indisponibles, Olise incertain (relevé le 27/11 à 3h, avant-matchs du 26/11)",
            "src": "https://www.sportsmole.co.uk/football/hamburger-sv/bundesliga-title-race/preview/hamburger-sv-vs-bayern-prediction-team-news-lineups_609927.html"},
    },
    "ucl": {}, "uel": {}, "uecl": {},
}
