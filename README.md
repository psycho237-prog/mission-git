# Mission Git

**Français** · [English](README.en.md)

Mini-jeu d'atelier pour apprendre les pull requests, les checks GitHub Actions et la résolution de conflits Git.

## Le scénario

Une équipe de secours doit partir en mission, mais son tableau de missions est incomplet. Chaque participant reçoit une **carte de défi** : une mission précise à ajouter dans `missions.json`. Chaque carte contient **un défaut volontaire** qu'il faut repérer et corriger pour que le robot de vérification (GitHub Actions) accepte la pull request (PR).

Comme tout le monde remplace le même bloc `TODO`, Git finit par provoquer un **conflit** : c'est le cœur du jeu.

## Parcours du participant

1. **Forkez** le dépôt sur votre compte GitHub (bouton *Fork*).
2. **Créez une branche** depuis l'état initial de `main` de votre fork :

   ```bash
   git clone https://github.com/<votre-pseudo>/mission-git.git
   cd mission-git
   git switch -c mission/<votre-prenom>
   ```

3. **Découvrez votre carte** en ouvrant une PR (même sans rien changer) ou, plus rapide, en local :

   ```bash
   python3 check_missions.py --auteur <votre-pseudo>
   ```

   Le message affiche votre pseudo, votre carte, la mission à ajouter (avec son défaut) et un indice.

4. **Remplacez le bloc `TODO`** par la mission de votre carte, telle qu'elle est affichée.

5. **Ouvrez votre PR** vers `main` et **lisez le résultat du workflow** dans l'onglet *Checks* : elle sera rouge, c'est normal.

6. **Intégrez `main`** dans votre branche dès que GitHub signale un conflit (un autre participant a fusionné avant vous) et **résolvez le conflit** en conservant les missions des autres.

7. **Corrigez le défaut** de votre carte à l'aide des indices, puis poussez :

   ```bash
   git add missions.json
   git commit -m "Corrige la mission de ma carte"
   git push
   ```

8. **Vérifiez** que la PR n'a plus de conflit et que le workflow est **vert**.

> Règle d'or : ne modifiez que `missions.json`. Ne touchez jamais à `check_missions.py`, `cartes.json`, `update_leaderboard.py` ni aux workflows : c'est le validateur de la branche de base qui est exécuté, et une PR qui touche ces fichiers est refusée en revue.

## Votre carte de défi

### Comment elle est attribuée

L'attribution est déterministe, sans hasard et sans service externe :

```
total = somme des codes Unicode des caractères du pseudo, en minuscules
carte = cartes[total % nombre_de_cartes]
```

Autrement dit : on additionne les codes des lettres de votre pseudo, on divise par le nombre de cartes et on garde le reste. **Le même pseudo donne toujours la même carte.** Le workflow utilise le pseudo de l'auteur de la PR (`github.event.pull_request.user.login`), il n'y a donc rien à déclarer.

Les cartes disponibles sont dans `cartes.json` : `colis-perdu`, `pont-effondre`, `radio-secours` et `avalanche`. Plusieurs personnes peuvent recevoir la même carte : leurs missions portent le même titre mais des identifiants différents (le pseudo est inclus dans l'identifiant), donc tout reste compatible.

### Le message du workflow

À chaque exécution, le workflow affiche :

- le **pseudo** utilisé pour l'attribution ;
- la **carte** attribuée (identifiant et titre) ;
- la **mission à ajouter**, avec son défaut volontaire ;
- le **défaut trouvé** et un **indice** pour le corriger.

## Règles de validation

Le script `check_missions.py` vérifie que :

- `missions.json` existe et contient du JSON valide ;
- la clé `missions` est une liste d'**au moins deux missions** ;
- chaque mission possède un `id` non vide, un `title` non vide et une `difficulty` entière valant **1, 2 ou 3** ;
- l'identifiant `TODO` a bien été remplacé ;
- les identifiants sont **uniques** ;
- aucune mission déjà présente sur la branche de base n'a été **supprimée** : le workflow compare `missions.json` à celui de `main` (`--base`) ;
- la **mission de votre carte** est présente, avec l'identifiant attendu `<carte>-<pseudo>`, et **sans défaut**.

Tant que le défaut de votre carte est présent, le check reste rouge, même si le reste du fichier est valide.

### Exemple de mission corrigée

Pour un pseudo `david`, la carte `colis-perdu` donne :

```json
{
  "missions": [
    {
      "id": "demo",
      "title": "Mission de démonstration",
      "difficulty": 1
    },
    {
      "id": "colis-perdu-david",
      "title": "Retrouver un colis égaré en zone urbaine",
      "difficulty": 2
    }
  ]
}
```

Les deux missions sont valides et les identifiants sont uniques.

## Indices progressifs

Commencez par l'indice 1. L'indice 2 est là si vous bloquez.

| Défaut | Indice 1 | Indice 2 |
| --- | --- | --- |
| Difficulté hors limites | Le champ `difficulty` doit être un nombre entier, pas un texte. | Seules les valeurs 1, 2 et 3 sont acceptées : remplacez 4 par 1, 2 ou 3. |
| Titre vide | Une mission sans titre ne peut pas être affichée à l'équipe de secours. | Remplissez `title` avec une phrase courte qui décrit la mission. |
| Identifiant vide | Chaque mission a besoin d'un identifiant pour être retrouvée. | Remplissez `id` avec un texte unique, par exemple `radio-secours-<votre-pseudo>`. |
| Identifiant dupliqué | Deux missions ne peuvent pas partager le même identifiant. | L'identifiant `demo` est déjà pris : choisissez-en un autre, par exemple `avalanche-<votre-pseudo>`. |

En dehors du champ défectueux, **ne changez rien** : l'identifiant proposé (`<carte>-<pseudo>`) doit rester tel quel, sauf si le défaut porte justement sur l'identifiant.

## Comprendre le conflit Git

Un conflit apparaît quand deux branches modifient **la même ligne** du même fichier. Ici, tout le monde remplace le même bloc `TODO` : Git ne peut pas décider quelle version garder et s'arrête.

```bash
git fetch origin
git merge origin/main
```

Git affiche alors :

```
CONFLICT (content): Merge conflict in missions.json
Automatic merge failed; fix conflicts and then commit the result.
```

Ouvrez `missions.json` : Git a inséré des marqueurs.

```
<<<<<<< HEAD
      "id": "colis-perdu-david",
      ...
=======
      "id": "radio-secours-alice",
      ...
>>>>>>> origin/main
```

- `<<<<<<< HEAD` ouvre **votre** version (votre branche) ;
- `=======` sépare les deux versions ;
- `>>>>>>> origin/main` ferme la version venue de `main`.

Vous devez **garder les deux missions** (la vôtre et celles des autres), supprimer les trois lignes de marqueurs et vérifier que les virgules et les accolades du JSON restent correctes.

Après résolution :

```bash
git add missions.json
git commit -m "Résout le conflit des missions"
git push
```

Le check se relance automatiquement (`synchronize`) : il doit repasser au vert.

## Déroulé de l'atelier (30 minutes)

| Durée | Étape |
| --- | --- |
| 0-3 min | Accueil, scénario de l'équipe de secours, présentation du dépôt. |
| 3-6 min | Démonstration : fork, branche, PR, lecture du message de carte. |
| 6-14 min | Chacun fork, crée sa branche, ajoute la mission de sa carte et ouvre sa PR. Les checks sont rouges : c'est prévu. |
| 14-17 min | L'animateur fusionne la première PR : le conflit apparaît chez les autres. |
| 17-25 min | Chacun intègre `main`, résout le conflit en gardant toutes les missions, corrige le défaut de sa carte et pousse. |
| 25-30 min | Fusion des PR restantes, classement, bilan : PR, checks, conflits, bonnes pratiques. |

## Classement automatique

Chaque PR fusionnée qui a passé le check **Mission check** rapporte **3 points** à son auteur GitHub. Le classement est écrit automatiquement dans `leaderboard.json` par le workflow **Classement**.

### Règles de score

- **3 points** par PR fusionnée dont le check de validation est vert au moment de la fusion.
- Les scores existants sont **conservés** : le fichier est complété, jamais réinitialisé.
- Une PR n'est comptée **qu'une seule fois** : son numéro est enregistré dans `prs`, donc rejouer le workflow ne rajoute rien.
- Le classement est **trié par points décroissants** ; à égalité, les logins sont rangés par ordre alphabétique.
- Une PR fusionnée sans check vert — ou sans check du tout, par exemple depuis un fork sans approbation — rapporte **0 point** : le workflow affiche un avertissement, se termine au vert et ne modifie rien.
- Même chose pour une PR qui modifie **autre chose que `missions.json`** (validateur, cartes, workflows) : elle ne rapporte aucun point.

Format du fichier :

```json
{
  "entries": [
    { "login": "bob", "points": 6, "prs": [13, 14] },
    { "login": "alice", "points": 3, "prs": [12] }
  ]
}
```

### Consulter le classement

- Ouvrez `leaderboard.json` dans le dépôt : la liste est à jour et déjà triée.
- Onglet **Actions** → workflow **Classement** : chaque exécution indique les points attribués et l'auteur de la PR.
- L'historique du dépôt montre les commits automatiques « Met à jour le classement (PR #12) ».

## Vérifier le projet en local

```bash
python3 check_missions.py --auteur <votre-pseudo>
python3 test_parcours.py
```

Le `missions.json` livré **échoue volontairement** : il contient encore l'identifiant `TODO`. C'est le point de départ du jeu.

`test_parcours.py` rejoue tout le parcours dans un dépôt Git jetable : état de départ rouge, carte de deux participants, conflit, résolution, refus d'une suppression de mission et classement. Il ne touche ni au dépôt ni au réseau.

## Structure du projet

```
mission-git/
├── README.md
├── README.en.md
├── .gitignore
├── missions.json
├── cartes.json
├── check_missions.py
├── leaderboard.json
├── update_leaderboard.py
├── test_parcours.py
└── .github/
    ├── CODEOWNERS
    └── workflows/
        ├── mission-check.yml
        └── leaderboard.yml
```

Aucune dépendance externe, aucun secret, aucun déploiement : Python 3 et Git suffisent.
