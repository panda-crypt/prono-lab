# Tests historiques de Prono Lab

Scripts qui produisent les chiffres affichés dans l'onglet *Fiabilité* (7 saisons, 2019-2026, 5 grands championnats).
Ils sont **chronologiques** : chaque prédiction n'utilise que les matchs joués avant elle, et les corrections des paris verts
du test hors échantillon ne sont apprises que sur les saisons précédentes.

## Données

Résultats et cotes (Pinnacle avant-match et clôture, Bet365, moyenne du marché) de football-data.co.uk, téléchargés par la
tâche GitHub « Cotes historiques » dans la branche `history` :

```
mkdir -p backtest/data
for f in $(git ls-tree --name-only origin/history); do git show origin/history:$f > backtest/data/$f; done
cd backtest && pip install pandas numpy
```

## Scripts (à lancer dans `backtest/`, dans cet ordre)

| Script | Ce qu'il mesure |
|---|---|
| `bt_value.py` | Paris dorés : cote d'un bookmaker au moins 2-4 % au-dessus de la juste cote Pinnacle ; rendement et CLV |
| `bt_model.py` | Modèle de buts recalculé chaque journée (écrit `model.pkl`, utilisé par les suivants) |
| `bt_tickets.py` | Qualité du modèle face au marché, valeur selon le modèle seul, paris verts, tickets et jackpots |
| `bt_markets.py` | Calibration des marchés (mi-temps, buts par équipe, combinés du match…) |
| `bt_green_oos.py` | Paris verts hors échantillon et facteurs de correction intégrés à l'application (`HIST_F`) |
| `bt_cups.py` | Écart de niveau entre divisions (promus et relégués, 7 saisons) : constantes `DIV_LEVEL` des coupes nationales |
| `bt_meta.py` | Laboratoire Metabet : astrologie, numérologie, cartomancie face au hasard équivalent |

Limite : le modèle des scripts n'utilise que les buts (les xG match par match ne sont pas disponibles pour le passé),
alors que l'application y ajoute les xG de la saison ; il est donc un peu moins bon que celui de l'application.

Coupes nationales (`bt_cups.py`, octobre 2026) : retour vers la moyenne d'une saison à l'autre β = 0,713 ; écarts
(log buts marqués / encaissés) : Premier League → Championship 1,04 ± 0,07 ; Championship → League One 0,63 ± 0,05 ;
League One → League Two 0,42 ± 0,05 ; LaLiga 0,73 ± 0,05 ; Serie A 0,76 ± 0,06 ; Bundesliga 0,73 ± 0,07 ; Ligue 1 0,80 ± 0,06.
Promus et relégués donnent des mesures proches (ex. Premier League 1,08 et 1,01), signe que le biais de sélection est bien corrigé.
Le facteur de rotation `CUP_SHRINK = 0,8` vient de 11 matchs de coupe d'octobre 2026 comparés aux cotes (bet365 et meilleures
cotes allemandes) : mesure **dans l'échantillon** et provisoire, sans test historique des coupes (pas de données de coupe chez football-data.co.uk).
