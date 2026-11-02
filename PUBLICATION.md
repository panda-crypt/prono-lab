# Mettre Prono Lab sur Google Play

Deux applications sortent de ce dépôt à chaque version :

| Fichier | Pour qui | Identifiant |
| --- | --- | --- |
| `prono-lab.apk` | vous seul : application complète (Metabet, clé de cotes, ouverture des bookmakers) | `fr.pronolab.app` |
| `prono-lab-public.apk` | testeurs de la bêta, installation manuelle | `fr.pronolab.analyse` |
| `prono-lab-google-play.aab` | à déposer dans la Google Play Console | `fr.pronolab.analyse` |

La version publique n'a ni Metabet, ni clé de cotes personnelle, ni bouton vers les sites de paris, et demande la majorité au premier lancement.

## Étapes à faire vous-même

1. **Créer le compte développeur** sur https://play.google.com/console : 25 $ une fois, pièce d'identité, adresse, téléphone. Choisir un compte « personnel ».
2. **Activer la page web** (politique de confidentialité) : sur GitHub, dépôt `prono-lab` → Settings → Pages → Source « Deploy from a branch », branche `main`, dossier `/docs`. L'adresse sera https://panda-crypt.github.io/prono-lab/confidentialite.html.
3. **Créer l'application** dans la Play Console : nom, langue français, « Application », « Gratuite ».
4. **Remplir la fiche et les questionnaires** avec les textes de `play/FICHE.md`.
5. **Test fermé obligatoire** : un compte personnel récent doit faire tester l'application par **au moins 12 personnes pendant 14 jours d'affilée** avant de pouvoir la publier.
   - Play Console → Tests → Test fermé → créer une liste de testeurs (leurs adresses Gmail).
   - Déposer `prono-lab-google-play.aab` (dernière version sur la page des versions GitHub).
   - Envoyer le lien d'inscription aux testeurs : ils doivent l'accepter et installer l'application depuis le Play Store.
6. **Demander l'accès à la production** après les 14 jours, en répondant au questionnaire sur le test.
7. **Abonnement** (plus tard, après la bêta) : 6,99 €/mois ou 49,99 €/an. Il faudra ajouter la facturation Google Play dans l'application et créer l'abonnement dans la Play Console (« Monétiser »).

## Clé d'envoi

Google signe lui-même l'application publiée (« signature d'application par Google Play »). Le fichier `.aab` est signé avec une clé d'envoi, qui sert seulement à prouver que l'envoi vient de vous. Par défaut, c'est la clé de l'application perso, déjà dans ce dépôt public. Pour une clé à part, ajoutez dans GitHub → Settings → Secrets → Actions `UPLOAD_KS_B64` (keystore en base64, alias `upload`) et `UPLOAD_KS_PASS`, **avant** le premier dépôt dans la Play Console.

## Avant de passer en payant

- Rendre le code privé : le dépôt est public, donc n'importe qui peut copier l'application. Il faudra séparer le code (privé) des données (publiques).
- Données sous licence et serveur automatique : voir le plan commercial.
- Scores en direct dans la version publique : ils demandent un flux de scores payé par vous (la version perso utilise votre clé).
