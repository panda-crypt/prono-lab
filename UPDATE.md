# Mise à jour des données de Prono Lab

Procédure suivie par la tâche planifiée (lundi et vendredi). L'application Android télécharge `data.json`
depuis la branche `main` de ce dépôt : publier un nouveau `data.json` suffit, aucune recompilation de l'APK n'est nécessaire.

**Règle d'or : ne jamais inventer un résultat, une statistique ou une cote.** Si une source ne répond pas,
garder les données précédentes de ce championnat et le signaler dans le message de commit.

## Fichiers à mettre à jour

| Fichier | Contenu |
|---|---|
| `raw/l1.txt`, `raw/pl.txt`, `raw/liga.txt`, `raw/sa.txt`, `raw/bl.txt` | Une ligne par match : `D Mon YYYY\|HH:MM\|Domicile\|Extérieur\|score` (heure du Royaume-Uni telle qu'affichée par statz.ai ; score vide si non joué, sinon `2-1`) |
| `raw/meta.py` | `xg` (MJ, xG pour, xG contre), `xgAsOf`, `odds` (cotes 1/N/2 des matchs à venir) |

Les noms d'équipes doivent être **exactement** ceux de statz.ai (ceux déjà présents dans les fichiers).

## Étapes

1. **Résultats et calendrier.** Pour chaque championnat, lire `https://statz.ai/competitions/<slug>/fixtures`
   (slugs : `ligue-1`, `premier-league`, `la-liga`, `serie-a`, `bundesliga`). Si l'outil refuse l'URL,
   faire d'abord une recherche web « statz.ai <championnat> fixtures 2026/2027 » puis ouvrir le lien trouvé.
   - Ajouter le score de chaque match joué depuis la dernière mise à jour.
   - Ajouter les matchs à venir des 12 prochains jours qui manquent. Inutile de garder plus loin.
   - Un match reporté : supprimer sa ligne s'il n'a plus de date.
2. **xG.** Lire `https://statz.ai/competitions/<slug>/xg` (même méthode) et mettre à jour `xg` et `xgAsOf` dans `raw/meta.py`.
3. **Cotes.** Chercher les cotes 1/N/2 des matchs à venir (par ex. les articles hebdomadaires de rg.org « … picks / odds »,
   oddscalendar.com, ou tout comparateur lisible). Une seule source par match ; noter le bookmaker.
   Cotes américaines : `+150` → 2,50 ; `-200` → 1,50 (formule : `+X` → 1 + X/100, `-X` → 1 + 100/X).
   Supprimer les cotes des matchs déjà joués (le script les ignore de toute façon).
4. **Construire et vérifier.**
   ```
   python3 build_data.py "AAAA-MM-JJTHH:MM" "AAAA-MM-JJ"   # date/heure de Paris de la mise à jour, puis date de relevé des cotes
   ```
   Le script s'arrête si une équipe n'a pas de xG ou de saison précédente. Vérifier ensuite sur une source officielle
   (classement du championnat) que les points des 3 premiers et du dernier correspondent aux résultats saisis.
5. **Publier.** `git add raw data.json && git commit -m "Données du JJ/MM : …" && git push origin main`.
   Ne pas modifier `app.html` ni `android/` (cela relancerait la compilation de l'APK).

## Résumé à écrire en fin de tâche

Une ou deux phrases : nombre de résultats ajoutés, matchs à venir avec cotes, championnats non mis à jour et pourquoi.
