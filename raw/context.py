"""Contexte des prochains matchs : absences importantes, équipes remaniées, matchs sans enjeu.

Rempli à chaque mise à jour (voir UPDATE.md, étape « Contexte »). Ne jamais inventer : chaque entrée cite sa source.
Clés : noms des équipes exactement comme dans raw/<championnat>.txt.
  lvl = "alerte" : le pronostic du modèle est faussé (ex. buteur et meneur du favori forfaits, équipe B alignée) ;
                   le match est retiré des paris verts, des tickets et des jackpots.
  lvl = "info"   : à savoir, sans effet sur les propositions (ex. un titulaire incertain).
"""
CHECKED_AT = "2026-10-26T09:00"   # date et heure de Paris de la dernière vérification
CONTEXT = {
    # exemple : "l1": {("Paris Saint Germain", "Olympique Lyonnais"): {"lvl": "alerte", "why": "…", "src": "https://…"}},
    "l1": {
        ("Paris Saint Germain", "Olympique Lyonnais"): {"lvl": "alerte",
            "why": "PSG sans Dembélé, Kvaratskhelia, Marquinhos et Nuno Mendes (blessés). Lyon sans Openda, Tagliafico, Ouédraogo (blessés) ni Nakamura (suspendu). Match lundi 26/10 à 20h30.",
            "src": "https://www.ruedesjoueurs.com/pronostic/psg-lyon-5802972.html"},
    },
    "pl": {},
    "liga": {},
    "sa": {},
    "bl": {},
}
