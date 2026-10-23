# Prono Lab

Application Android de pronostics football pour la Ligue 1, la Premier League, la Liga, la Serie A et la Bundesliga.

**Installer :** sur votre téléphone, ouvrez la page [Releases](../../releases/latest) et touchez `prono-lab.apk`.
Android vous demandera d'autoriser l'installation depuis cette source : acceptez pour ce téléchargement.

## Ce que fait l'application

- **Matchs** : les rencontres des 10 prochains jours avec probabilités 1-N-2, buts attendus et pronostic principal ; classement avec bilans domicile/extérieur, forme et xG.
- **Valeur** : les paris dont la cote dépasse la probabilité estimée (calcul prudent : 60 % modèle, 40 % marché), avec la mise conseillée.
- **Analyse** : n'importe quelle affiche, tous les marchés (double chance, plus/moins de buts, les deux marquent, scores exacts), ajustements manuels.
- **Mes paris** : suivi des paris, réglement automatique quand le résultat arrive, bankroll, rendement, limites hebdomadaires et alertes.
- **Fiabilité** : test du modèle sur les matchs déjà joués de la saison (favori juste, score Brier, calibration).

## Mises à jour

L'application télécharge `data.json` au démarrage (et via le bouton « Mettre à jour »).
Une tâche planifiée met ce fichier à jour deux fois par semaine en suivant [UPDATE.md](UPDATE.md).
Sans connexion, l'application garde les dernières données reçues. Vos paris restent sur votre téléphone.

## Modèle

xG et buts de la saison (récence pondérée, force des adversaires), mélangés avec la saison 2025-26,
avantage du terrain propre à chaque championnat, loi de Poisson corrigée de Dixon-Coles.

Jouer comporte des risques : endettement, isolement, dépendance. Joueurs Info Service : 09 74 75 13 13.
