# Mise à jour des données de Prono Lab

Procédure suivie par la tâche planifiée (lundi, mercredi et vendredi). L'application Android télécharge `data.json`
depuis la branche `main` de ce dépôt : publier un nouveau `data.json` suffit, aucune recompilation de l'APK n'est nécessaire.

**Règle d'or : ne jamais inventer un résultat, une statistique ou une cote.** Si une source ne répond pas,
garder les données précédentes de ce championnat et le signaler dans le message de commit.

## Fichiers à mettre à jour

| Fichier | Contenu |
|---|---|
| `raw/l1.txt`, `raw/pl.txt`, `raw/liga.txt`, `raw/sa.txt`, `raw/bl.txt` | Une ligne par match : `D Mon YYYY\|HH:MM\|Domicile\|Extérieur\|score` (heure du Royaume-Uni telle qu'affichée par statz.ai ; score vide si non joué, sinon `2-1`, ou `2-1 (1-0)` avec le score à la mi-temps) |
| `raw/meta.py` | `xg` (MJ, xG pour, xG contre), `xgAsOf`, `odds` (cotes 1/N/2 des matchs à venir) |
| `raw/context.py` | Absences importantes, équipes remaniées, matchs sans enjeu des 4 prochains jours (avec source) |

Les noms d'équipes doivent être **exactement** ceux de statz.ai (ceux déjà présents dans les fichiers).

**Autres championnats** (Championship, League One/Two, Écosse, 2. Bundesliga, Serie B, LaLiga 2, Ligue 2, Eredivisie, Belgique,
Portugal, Turquie, Grèce) : le dossier `fd/` est mis à jour automatiquement deux fois par jour par la tâche GitHub
« Autres championnats » (football-data.co.uk), qui reconstruit aussi `data.json`. Ne pas modifier `fd/` à la main ;
`build_data.py` l'intègre de lui-même. Faire `git pull --rebase` juste avant de publier.

## Étapes

1. **Résultats et calendrier.** Pour chaque championnat, lire `https://statz.ai/competitions/<slug>/fixtures`
   (slugs : `ligue-1`, `premier-league`, `la-liga`, `serie-a`, `bundesliga`). Si l'outil refuse l'URL,
   faire d'abord une recherche web « statz.ai <championnat> fixtures 2026/2027 » puis ouvrir le lien trouvé.
   - Ajouter le score de chaque match joué depuis la dernière mise à jour.
     Quand la source le donne, ajouter le score à la mi-temps entre parenthèses : `2-1 (1-0)`. Il sert à régler les paris
     « mi-temps » ; sans lui, ces paris restent en attente (ne jamais l'inventer).
   - Ajouter les matchs à venir des 12 prochains jours qui manquent. Inutile de garder plus loin.
   - Un match reporté : supprimer sa ligne s'il n'a plus de date.
2. **xG.** Lire `https://statz.ai/competitions/<slug>/xg` (même méthode) et mettre à jour `xg` et `xgAsOf` dans `raw/meta.py`.
3. **Cotes.** Chercher les cotes 1/N/2 des matchs à venir (par ex. les articles hebdomadaires de rg.org « … picks / odds »,
   oddscalendar.com, ou tout comparateur lisible). Une seule source par marché et par match ; noter le bookmaker.
   Quand elles sont disponibles, ajouter aussi plus/moins de 2,5 buts et « les deux équipes marquent » :
   `("Domicile","Extérieur"): {"1x2": ("Bookmaker", [c1, cN, c2]), "ou": ("Bookmaker", [plus, moins]), "btts": ("Bookmaker", [oui, non])}`
   (l'ancienne forme `("Bookmaker", [c1, cN, c2])` reste acceptée). Préférer la meilleure cote disponible.
   Cotes américaines : `+150` → 2,50 ; `-200` → 1,50 (formule : `+X` → 1 + X/100, `-X` → 1 + 100/X).
   Supprimer les cotes des matchs déjà joués (le script les ignore de toute façon).
4. **Coupes d'Europe** (`raw/ucl.txt`, `raw/uel.txt`, `raw/uecl.txt`, `raw/euro.py`).
   - Ligue des champions : `https://statz.ai/competitions/champions-league/fixtures` (heures du Royaume-Uni, fichier marqué `#tz=uk`).
   - Ligue Europa et Ligue Conférence : articles uefa.com « all the league phase fixtures and results » (liens dans `raw/euro.py`,
     `SOURCES`), heures de Paris (fichiers marqués `#tz=paris`, 21:00 quand l'heure n'est pas précisée).
   - Ajouter les scores joués et les matchs des 16 prochains jours. À partir des barrages, ajouter les nouveaux matchs
     dans le même fichier (les clubs doivent figurer dans `CLUBS`, avec leur pays et, pour les 5 grands championnats, leur id statz).
   - Cotes des matchs européens : dictionnaire `ODDS` de `raw/euro.py`, par compétition :
     `ODDS = {"ucl": {("Domicile","Extérieur"): {"1x2": ("Bookmaker", [c1, cN, c2])}}}`.
   - Coefficients des pays (`COUNTRY_COEF`) : à rafraîchir une fois par mois depuis Wikipédia « UEFA coefficient ».
5. **Contexte des prochains matchs** (`raw/context.py`) — le « vérificateur » : le modèle ignore les absences et les compositions.
   Pour chaque match des **4 prochains jours** (championnats et coupes d'Europe) :
   - Chercher les nouvelles d'avant-match (conférence de presse, sites des clubs, L'Équipe, BBC Sport, Marca, Gazzetta, Kicker,
     ou une page « injuries / team news » de la journée). Une recherche par championnat et par journée suffit le plus souvent.
   - `"alerte"` **seulement** si une information confirmée fausse nettement le pronostic :
     au moins deux titulaires majeurs absents dans la même équipe (meilleur buteur, meneur, gardien titulaire, capitaine),
     équipe largement remaniée annoncée (rotation avant un match plus important, équipe réserve),
     ou match sans enjeu pour une équipe (déjà qualifiée/éliminée et qui l'a annoncé).
   - `"info"` pour une absence notable seule ou un doute sur un titulaire.
   - Rien à signaler : ne rien écrire. **Ne jamais inventer ni supposer une absence** ; chaque entrée cite l'URL de sa source.
   - Effacer les entrées des matchs joués, remplir `CHECKED_AT` (date et heure de Paris de la vérification).
   - Format : `CONTEXT = {"l1": {("Domicile", "Extérieur"): {"lvl": "alerte", "why": "Dembélé et Vitinha forfaits", "src": "https://…"}}}`
     (noms exactement comme dans `raw/<championnat>.txt`).
6. **Construire et vérifier.**
   ```
   python3 build_data.py "AAAA-MM-JJTHH:MM" "AAAA-MM-JJ"   # date/heure de Paris de la mise à jour, puis date de relevé des cotes
   ```
   Le script s'arrête si une équipe n'a pas de xG ou de saison précédente. Vérifier ensuite sur une source officielle
   (classement du championnat) que les points des 3 premiers et du dernier correspondent aux résultats saisis.
7. **Publier.** `git add raw data.json && git commit -m "Données du JJ/MM : …" && git push origin main`.
   Ne pas modifier `app.html` ni `android/` (cela relancerait la compilation de l'APK).

## Résumé à écrire en fin de tâche

Une ou deux phrases : nombre de résultats ajoutés, matchs à venir avec cotes, alertes de contexte ajoutées, championnats non mis à jour et pourquoi.
