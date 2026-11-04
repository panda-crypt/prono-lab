# Prototype : modèle européen séparé (04/11/2026)

Branche d'essai, **rien n'est branché dans l'application**. Les championnats nationaux ne sont pas concernés (vérifié : Ligue 1, Brier 0,578 avant et après).

## Ce qui a été testé

Chaque jour de match européen, les paramètres sont réappris **uniquement sur les matchs européens antérieurs**, puis on prédit les matchs du jour (117 matchs évalués sur 153 joués, 7 journées ; il faut 30 matchs antérieurs pour commencer, comme dans l'onglet Fiabilité).

| Modèle | Principe |
|---|---|
| `cur` | Modèle européen actuel de l'application |
| `lien` | Modèle actuel + 25 clubs reliés à leur championnat national (`liens_domestiques.patch`) |
| A | Notation européenne unique : force = a·(coefficient du pays) + b·exp(c·pays)·(note nationale) + effet club appris en coupe d'Europe. `exp(c·pays)` pondère la note nationale par le niveau du championnat |
| B | Mélange de A et du modèle actuel, proportion apprise sur les matchs déjà joués |
| C | A + tendance aux buts (attaque et défense nationales) + forme (écart de buts sur les 5 derniers matchs nationaux) |

Le vrai classement Elo des clubs (clubelo.com) n'a pas pu être utilisé : le site est bloqué depuis l'environnement de travail de Claude. A est donc une notation construite avec les données déjà présentes dans le dépôt.

## Résultats (`resultats.txt`)

| Modèle | Brier 1N2 | Log-loss | Brier +2,5 buts | Favori juste | Écart de Brier avec l'actuel [IC 90 %] |
|---|---|---|---|---|---|
| actuel | 0,552 | 0,940 | 0,224 | 56 % | — |
| lien | 0,548 | 0,926 | 0,226 | 58 % | −0,004 [−0,030 ; +0,022] |
| A | 0,551 | 0,933 | 0,226 | 57 % | −0,001 [−0,029 ; +0,027] |
| B | 0,556 | 0,940 | 0,225 | 54 % | +0,004 [−0,014 ; +0,023] |
| C | 0,550 | 0,934 | 0,226 | 56 % | −0,002 [−0,030 ; +0,026] |

- **Aucune différence mesurable** : tous les écarts sont inférieurs à 0,005, alors que l'incertitude est de ±0,03. 117 matchs ne suffisent pas pour départager les modèles.
- Sur les 9 matchs du 3/11 avec cotes : marché 0,388, actuel 0,500, A 0,453, C 0,447. Trop peu de matchs pour conclure.
- Sur les 36 matchs du 4 et 5/11 avec cotes : écart moyen au marché de 8,4 points pour le modèle actuel, contre 9,1 (lien), 9,7 (A) et 9,5 (C). **Les nouveaux modèles s'éloignent du marché.**
- Le poids du niveau de championnat appris (`c` ≈ 0,18) est trop faible : Benfica reste à 91 % contre Lech (marché 70 %) et AEK à 19 % contre le Real (marché 12 %). Avec une seule saison de coupes d'Europe, le modèle ne peut pas apprendre seul l'écart de niveau entre les championnats.
- La forme n'apporte rien (`phi` ≈ −0,02, proche de 0) ; la tendance aux buts un peu (`tau` ≈ 0,18), sans gain visible sur le marché des +2,5 buts.

## Conclusion

Avec les données disponibles, **aucune des trois options ne fait mieux que le modèle actuel** ; elles font même un peu moins bien face aux cotes des prochains matchs. Ne rien brancher.

Ce qu'il manque : une mesure de niveau qui compare les championnats sur plusieurs saisons (Elo de clubelo.com, ou les résultats européens des saisons passées). Deux moyens de l'obtenir :
1. autoriser le domaine `api.clubelo.com` dans les réglages de Claude (Réglages > Capacités), pour tester ici ;
2. ou ajouter le téléchargement à une tâche GitHub (modification de `.github/`, accord nécessaire).

## Refaire le test

```
python3 build_app.py && cp dist/index.html /tmp/new.html               # données actuelles
git apply proto/liens_domestiques.patch && python3 build_data.py "AAAA-MM-JJTHH:MM" "AAAA-MM-JJ" && python3 build_app.py && cp dist/index.html /tmp/exp.html
cd proto && node harness.js /tmp/new.html cur.json && node harness.js /tmp/exp.html feat.json && python3 models.py .
```
`hist_odds.json` : cotes 1N2 retrouvées dans l'historique git de `raw/euro.py`.
