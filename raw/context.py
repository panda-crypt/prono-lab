"""Contexte des prochains matchs : absences importantes, équipes remaniées, matchs sans enjeu.

Rempli à chaque mise à jour (voir UPDATE.md, étape « Contexte »). Ne jamais inventer : chaque entrée cite sa source.
Clés : noms des équipes exactement comme dans raw/<championnat>.txt.
  lvl = "alerte" : le pronostic du modèle est faussé (ex. buteur et meneur du favori forfaits, équipe B alignée) ;
                   le match est retiré des paris verts, des tickets et des jackpots.
  lvl = "info"   : à savoir, sans effet sur les propositions (ex. un titulaire incertain).
"""
CHECKED_AT = "2026-11-27T08:50"   # date et heure de Paris de la dernière vérification
CONTEXT = {
 "l1": {
    ('Paris Saint Germain', 'Lorient'): {"lvl": 'alerte', "why": 'PSG : Doué et Kvaratskhelia absents (croisés), Dembélé et Nuno Mendes ménagés après la Roma', "src": 'https://paris-supporters.fr/2026/11/26/match-psg/psg-lorient-tout-ce-quil-faut-savoir-avant-le-retour-au-parc-samedi-116490.html'},
    ('Auxerre', 'Olympique Marseille'): {"lvl": 'info', "why": 'OM : Cornelius absent, Højbjerg (malade) et Emerson incertains', "src": 'https://www.sportsmole.co.uk/football/aj-auxerre/preview/auxerre-vs-marseille-prediction-team-news-lineups_609973.html'},
    ('Olympique Lyonnais', 'Monaco'): {"lvl": 'info', "why": 'Monaco : Golovin et Ansu Fati absents, Coulibaly suspendu ; OL sans Morton ni Sulc', "src": 'https://www.rotowire.com/soccer/article/lyon-vs-monaco-prediction-predicted-lineups-team-news-148281'},
    ('Angers SCO', 'Lens'): {"lvl": 'info', "why": 'Lens : Edouard, Nawrocki et Aguilar absents, Cuisance incertain', "src": 'https://www.sportsmole.co.uk/football/angers/preview/angers-vs-lens-prediction-team-news-lineups_609963.html'},
    ('Le Mans', 'LOSC Lille'): {"lvl": 'info', "why": 'Lille : Igamane et Ueda blessés, Ethan Mbappé suspendu', "src": 'https://thefootballfaithful.com/le-mans-vs-losc-lille-prediction-betting-tips-28-11-2026/'},
    ('Toulouse', 'Rennes'): {"lvl": 'info', "why": 'Rennes : Thomasson suspendu, Rongier incertain', "src": 'https://www.sportsmole.co.uk/football/toulouse/preview/toulouse-vs-rennes-prediction-team-news-lineups_609972.html'},
 },
 "pl": {
    ('Arsenal', 'Manchester City'): {"lvl": 'alerte', "why": 'Arsenal : Saka et Zubimendi forfaits, Raya très incertain', "src": 'https://www.sportsmole.co.uk/football/arsenal/injury-news/injuries-and-suspensions/raya-saka-zubimendi-latest-arsenal-injury-suspension-list-vs-man-city_609872.html'},
    ('Everton', 'Liverpool'): {"lvl": 'alerte', "why": 'Liverpool : Ekitike et Gakpo forfaits, Gravenberch et Muñoz très incertains', "src": 'https://www.sportsmole.co.uk/football/liverpool/injury-news/injuries-and-suspensions/gakpo-gravenberch-munoz-latest-liverpool-injury-suspension-list-vs-everton_609909.html'},
    ('Nottingham Forest', 'Chelsea'): {"lvl": 'info', "why": 'Chelsea : Reece James absent, João Pedro probablement forfait', "src": 'https://www.fantasyfootballscout.co.uk/2026/11/26/fpl-gameweek-12-team-news-thursdays-live-injury-updates-2'},
    ('Manchester United', 'Brentford'): {"lvl": 'info', "why": 'Brentford : Igor Thiago suspendu, Collins, Hickey et Henry blessés ; MU sans Sesko, Baleba ni Ugarte', "src": 'https://www.sportsmole.co.uk/football/man-utd/preview/man-utd-vs-brentford-prediction-team-news-lineups_609874.html'},
    ('Sunderland', 'Tottenham Hotspur'): {"lvl": 'info', "why": 'Tottenham : Xavi Simons, Savio, Tel, Mudryk et Odobert absents', "src": 'https://www.sportsmole.co.uk/football/spurs/injury-news/injuries-and-suspensions/tonali-savio-tosin-latest-spurs-injury-suspension-list-vs-sunderland_609873.html'},
    ('Ipswich Town', 'Aston Villa'): {"lvl": 'info', "why": 'Villa : Onana et Ruggeri absents, Cash incertain', "src": 'https://www.sportsmole.co.uk/football/aston-villa/injury-news/injuries-and-suspensions/onana-cash-ruggeri-latest-aston-villa-injury-list-for-ipswich-clash_609808.html'},
 },
 "liga": {
    ('Deportivo La Coruña', 'FC Barcelona'): {"lvl": 'info', "why": 'Barça : Fermín suspendu, Balde blessé, Rodri très incertain', "src": 'https://www.sportsmole.co.uk/football/barcelona/injury-news/injuries-and-suspensions/yamal-rodri-balde-updates-barcelona-injury-suspension-list-vs-deportivo_609835.html'},
    ('Elche', 'Atlético Madrid'): {"lvl": 'info', "why": 'Atlético : Lookman et Cristian Romero absents', "src": 'https://www.sportsmole.co.uk/football/atletico-madrid/race-for-the-la-liga-title/preview/elche-vs-atletico-prediction-team-news-lineups_609930.html'},
    ('Real Madrid', 'Deportivo Alavés'): {"lvl": 'info', "why": 'Real : Rodrygo, Endrick, Asencio et Mendy absents', "src": 'https://www.sportsmole.co.uk/football/real-madrid/race-for-the-la-liga-title/preview/real-madrid-vs-alaves-prediction-team-news-lineups_609921.html'},
    ('Málaga', 'Athletic Club'): {"lvl": 'info', "why": 'Athletic : Guruzeta et Vivian absents', "src": 'https://www.livescore.com/en/news/football/laliga/predictions/laliga-predictions-all-10-matchday-14-games/'},
    ('Real Betis', 'Rayo Vallecano'): {"lvl": 'info', "why": 'Betis : Lo Celso et Ceballos incertains', "src": 'https://www.livescore.com/en/news/football/laliga/predictions/laliga-predictions-all-10-matchday-14-games/'},
    ('Valencia', 'Osasuna'): {"lvl": 'info', "why": 'Osasuna : Catena suspendu', "src": 'https://www.livescore.com/en/news/football/laliga/predictions/laliga-predictions-all-10-matchday-14-games/'},
 },
 "sa": {
    ('Sassuolo', 'Napoli'): {"lvl": 'alerte', "why": 'Napoli : Di Lorenzo, Lobotka, Buongiorno, Meret, Vergara et Badiashile absents', "src": 'https://www.thestatszone.com/sassuolo-vs-napoli-preview-team-news-prediction-241559'},
    ('Como', 'Juventus'): {"lvl": 'alerte', "why": 'Juve : Yıldız, Locatelli, K. Thuram et Kalulu absents ; Como sans Kean', "src": 'https://www.dazn.com/en-US/news/soccer/como-vs-juventus-preview-team-news-prediction-date-serie-a-2026-27/1uekysjytbdjd1f2lzi7t5hwyg'},
    ('Inter', 'Genoa'): {"lvl": 'info', "why": 'Inter : Çalhanoğlu et Bonny absents, Bastoni incertain', "src": 'https://www.thestatszone.com/inter-vs-genoa-preview-team-news-prediction-241530'},
    ('Cagliari', 'AC Milan'): {"lvl": 'info', "why": 'Milan : Modrić, Loftus-Cheek et Saelemaekers absents', "src": 'https://www.livescore.com/en/news/football/serie-a/predictions/serie-a-predictions-all-10-matchday-13-games/'},
    ('Lecce', 'Atalanta'): {"lvl": 'info', "why": 'Atalanta : gardien Carnesecchi absent', "src": 'https://www.livescore.com/en/news/football/serie-a/predictions/serie-a-predictions-all-10-matchday-13-games/'},
    ('Frosinone', 'Parma'): {"lvl": 'info', "why": "Frosinone : Raimondo absent jusqu'en janvier", "src": 'https://www.livescore.com/en/news/football/serie-a/predictions/serie-a-predictions-all-10-matchday-13-games/'},
 },
 "bl": {
    ('Hamburger SV', 'FC Bayern München'): {"lvl": 'alerte', "why": 'Bayern : Kane (plusieurs mois), Neuer, Davies, Gnabry et Saibari absents, Olise très incertain', "src": 'https://www.thestatszone.com/hamburg-vs-bayern-munich-preview-team-news-prediction-242696'},
    ('VfB Stuttgart', 'Eintracht Frankfurt'): {"lvl": 'info', "why": 'Francfort : Can Uzun incertain, Ngankam absent', "src": 'https://www.sportsmole.co.uk/football/stuttgart/preview/stuttgart-vs-frankfurt-prediction-team-news-lineups_609969.html'},
    ('SC Freiburg', 'RB Leipzig'): {"lvl": 'info', "why": 'Leipzig : Lukeba incertain, Gebel, Guiu et Ouedraogo absents', "src": 'https://www.thestatszone.com/freiburg-vs-rb-leipzig-preview-team-news-prediction-242727'},
 },
 "ucl": {}, "uel": {}, "uecl": {},
}
