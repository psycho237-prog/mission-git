# Mission Git

**Français** · [English](README.en.md)

Mini-jeu d'atelier de 30 minutes pour apprendre les pull requests, les checks GitHub Actions et la résolution de conflits Git.

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

## Consigne d'animation (indispensable)

> **Toutes les branches doivent être créées depuis le même état de `main` et toutes les PR doivent être ouvertes avant la fusion de la première PR.**

C'est cette simultanéité qui provoque le conflit pédagogique. Si les PR sont ouvertes et fusionnées une par une, aucun conflit n'apparaît et l'exercice perd son intérêt. Surveillez les PR et n'en fusionnez une que lorsque tout le monde a la sienne.

Option de secours si le conflit n'apparaît pas : demandez à **deux participants de modifier exactement le même bloc `TODO`** (c'est déjà le cas par construction : toutes les cartes remplacent ce bloc).

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

### Deux workflows séparés, par sécurité

| Workflow | Déclencheur | Permissions | Code exécuté |
| --- | --- | --- | --- |
| **Mission check** (validation) | PR `opened`, `synchronize`, `reopened` | `contents: read` | le validateur de la branche de base, appliqué au `missions.json` de la PR |
| **Classement** | `pull_request_target`, PR fermée **et fusionnée** | `contents: write` | uniquement la branche de base (`update_leaderboard.py`) |

Le workflow de validation n'exécute que le validateur et les cartes de la branche de base : il n'a donc **que la lecture**, et réécrire `check_missions.py` dans une PR ne change rien au verdict. Le workflow de classement possède l'écriture, mais il ne récupère **jamais** le code de la PR : `actions/checkout` pointe explicitement sur la branche de base, l'auteur et le numéro de PR sont lus dans l'événement, et le script exécuté est celui de la branche de base. Aucun code de PR ne tourne avec un jeton d'écriture.

> **Attention à la protection de branche :** le workflow de classement pousse un commit sur `main`. Si vous activez une règle qui interdit les poussées directes, autorisez le bot `github-actions[bot]` (ou le workflow) à pousser, sinon le classement restera bloqué.

## PR venant de forks : ce qu'il faut savoir

Le jeu fonctionne avec des forks, mais GitHub peut compliquer la validation :

- selon les réglages du dépôt, un workflow sur une PR venue d'un fork peut demander une **approbation manuelle** avant de démarrer ;
- sans exécution du workflow, il n'y a ni carte affichée ni check vert, donc **0 point** au classement ;
- le workflow de validation utilise la version du fichier de workflow de la PR (événement `pull_request`) : il faut donc que le dépôt de base ait le workflow avant les forks ; en revanche le validateur exécuté est bien celui de la branche de base.

Solution la plus simple et la plus sûre pour un atelier : les participants peuvent toujours exécuter `python3 check_missions.py --auteur <pseudo>` en local pour connaître leur carte et vérifier leur fichier, et l'animateur approuve les exécutions dans l'onglet **Actions**. Vérifiez aussi que l'option d'approbation des workflows de forks est réglée comme vous le souhaitez dans *Settings → Actions → General*.

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
├── GUIDE-ANIMATEUR.md
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

---

# Section réservée à l'animateur

Guide d'installation pas à pas (protection de branche, Code Owners, approbation des forks) : [GUIDE-ANIMATEUR.md](GUIDE-ANIMATEUR.md).

> Les solutions ci-dessous ne doivent pas être distribuées aux participants avant la fin de l'exercice.

## Solutions des cartes

Chaque carte contient **exactement un** défaut. La correction consiste à ne toucher que le champ fautif.

| Carte | Mission attendue | Défaut volontaire | Correction |
| --- | --- | --- | --- |
| `colis-perdu` <br>(ex. : `david`) | Retrouver un colis égaré en zone urbaine | `difficulty` vaut `4` | Mettre `1`, `2` ou `3` (valeur de la carte : `2`) |
| `pont-effondre` <br>(ex. : `rose`) | Rétablir un pont piéton effondré | `title` est vide | Écrire « Rétablir un pont piéton effondré » (ou tout titre non vide) |
| `radio-secours` <br>(ex. : `alice`) | Rétablir la radio de secours | `id` est vide | Mettre `radio-secours-<pseudo>` |
| `avalanche` <br>(ex. : `bob`) | Dégager une route bloquée par une avalanche | `id` vaut `demo` (duplicata) | Mettre `avalanche-<pseudo>` |

Exemple de fichier entièrement corrigé (pseudo `david`, carte `colis-perdu`) :

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

## Vérifier l'attribution avant l'atelier

Pour connaître la carte de chaque participant :

```bash
python3 check_missions.py --auteur <pseudo> | head -4
```

L'attribution est `somme des codes des lettres du pseudo, modulo 4`. Sur un grand nombre de pseudos, les quatre cartes sont utilisées de façon quasi égale ; deux participants peuvent partager une carte sans problème, leurs identifiants restent différents.

## Intégrité du jeu

- Demandez explicitement aux participants de **ne pas modifier** `check_missions.py`, `cartes.json`, `update_leaderboard.py` ni `.github/workflows/`.
- Activez aussi une **protection de branche** sur `main` exigeant le check `Vérifier les missions` avant fusion : une PR sans check reste bloquée.
- `.github/CODEOWNERS` désigne l'animateur comme propriétaire de `check_missions.py`, `cartes.json`, `update_leaderboard.py` et `.github/`. Activez la protection de branche avec **« Require a review from Code Owners »** : une PR qui touche ces fichiers demande alors l'accord de l'animateur, et les autres participants ne peuvent pas la fusionner seuls. Remplacez le login du fichier par celui de l'animateur.
- Le workflow de validation tourne avec `contents: read` uniquement : il ne peut rien écrire dans le dépôt.
