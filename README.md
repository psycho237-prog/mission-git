# Mission Git

**Français** · [English](README.en.md)

Mini-jeu d'atelier pour apprendre les pull requests, les checks GitHub Actions et la résolution de conflits Git.

## Le scénario

Une équipe de secours doit partir en mission, mais son tableau de missions est incomplet. Chaque participant reçoit une **carte de défi** : une mission précise à ajouter dans `missions.json`, avec **un défaut volontaire** à corriger pour que le robot de vérification (GitHub Actions) accepte la pull request (PR).

Comme tout le monde remplace le même bloc `TODO`, Git finit par provoquer un **conflit** : c'est le cœur du jeu.

## Le parcours en 6 étapes

### 1. Forkez, clonez, créez une branche

Cliquez sur **Fork**, puis :

```bash
git clone https://github.com/<votre-pseudo>/mission-git.git
cd mission-git
git switch -c mission/<votre-prenom>
```

### 2. Trouvez votre carte

Avec votre pseudo GitHub :

```bash
python3 check_missions.py --auteur <votre-pseudo>
```

La sortie affiche votre carte, la mission à ajouter **avec son défaut**, et un indice.

### 3. Remplacez le bloc `TODO`

Dans `missions.json`, remplacez la mission `TODO` par celle affichée, **sans la corriger pour l'instant**. Le robot la refusera : c'est voulu.

### 4. Poussez et ouvrez la PR

```bash
git add missions.json
git commit -m "Ajoute la mission de ma carte"
git push -u origin mission/<votre-prenom>
```

Ouvrez ensuite la PR vers `main` du dépôt d'origine. Dans l'onglet *Checks*, le check **Vérifier les missions** est **rouge** : le défaut de votre carte est encore là.

### 5. Intégrez `main` et résolvez le conflit

Dès qu'un autre participant a fusionné, GitHub signale un conflit sur votre PR.

Sur la page de votre fork, cliquez sur **Sync fork → Update branch**, puis :

```bash
git pull origin main
```

Sans le bouton, ajoutez le dépôt d'origine comme remote :

```bash
git remote add upstream https://github.com/<proprietaire>/mission-git.git
git fetch upstream
git merge upstream/main
```

Git s'arrête sur un conflit dans `missions.json`. La section [Résoudre le conflit](#résoudre-le-conflit-git) explique quoi faire : gardez **toutes** les missions.

### 6. Corrigez le défaut, poussez, vérifiez

Corrigez le champ fautif à l'aide des [indices](#indices-progressifs), puis :

```bash
python3 check_missions.py --auteur <votre-pseudo>   # doit être vert avant de pousser
git add missions.json
git commit -m "Corrige la mission de ma carte"
git push
```

Le check se relance tout seul : il doit être **vert** et la PR sans conflit.

> **Règle d'or :** ne modifiez que `missions.json`. C'est le seul fichier attendu dans votre PR.

## Votre carte de défi

Votre carte dépend de votre pseudo GitHub : **le même pseudo donne toujours la même carte**, il n'y a rien à déclarer. Le workflow lit l'auteur de la PR et affiche la mission attendue, son identifiant (`<carte>-<pseudo>`) et un indice.

Plusieurs participants peuvent recevoir la même carte : le pseudo fait partie de l'identifiant, donc les missions restent différentes.

## Règles de validation

Le fichier `missions.json` doit respecter ces règles :

- JSON valide, avec la clé `missions` contenant **au moins deux missions** ;
- pour chaque mission : `id` non vide et **unique**, `title` non vide, `difficulty` entier valant **1, 2 ou 3** ;
- le bloc `TODO` remplacé ;
- aucune mission déjà présente sur `main` **supprimée** : gardez les missions des autres ;
- **votre** mission présente, avec l'identifiant `<carte>-<pseudo>` et **sans défaut**.

Tant que le défaut de votre carte est là, le check reste rouge.

### Exemple de mission corrigée

Pseudo `david`, carte `colis-perdu` :

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

## Indices progressifs

Commencez par l'indice 1. L'indice 2 est là si vous bloquez.

| Défaut | Indice 1 | Indice 2 |
| --- | --- | --- |
| Difficulté hors limites | Le champ `difficulty` doit être un nombre entier, pas un texte. | Seules les valeurs 1, 2 et 3 sont acceptées : remplacez 4 par 1, 2 ou 3. |
| Titre vide | Une mission sans titre ne peut pas être affichée à l'équipe de secours. | Remplissez `title` avec une phrase courte qui décrit la mission. |
| Identifiant vide | Chaque mission a besoin d'un identifiant pour être retrouvée. | Remplissez `id` avec un texte unique, par exemple `radio-secours-<votre-pseudo>`. |
| Identifiant dupliqué | Deux missions ne peuvent pas partager le même identifiant. | L'identifiant `demo` est déjà pris : choisissez-en un autre, par exemple `avalanche-<votre-pseudo>`. |

En dehors du champ défectueux, **ne changez rien** : l'identifiant proposé doit rester tel quel, sauf si le défaut porte justement sur l'identifiant.

## Résoudre le conflit Git

Un conflit apparaît quand deux branches modifient **la même ligne** du même fichier. Ici, tout le monde remplace le même bloc `TODO` : Git ne peut pas choisir et s'arrête.

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
>>>>>>> upstream/main
```

- `<<<<<<< HEAD` ouvre **votre** version ;
- `=======` sépare les deux versions ;
- `>>>>>>>` ferme la version venue de `main` (`upstream/main`, ou `origin/main` si vous êtes passé par le bouton *Sync fork*).

**Gardez les deux missions** (la vôtre et celle des autres), supprimez les trois lignes de marqueurs et vérifiez les virgules et les accolades du JSON.

```bash
git add missions.json
git commit -m "Résout le conflit des missions"
git push
```

Le check se relance automatiquement : il doit repasser au vert.

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

Chaque PR fusionnée avec un check vert rapporte **3 points** à son auteur. Le classement est écrit automatiquement dans `leaderboard.json`.

- Une PR n'est comptée **qu'une seule fois**.
- Les scores existants sont conservés d'une PR à l'autre.
- Tri par points décroissants, puis par pseudo.
- **0 point** si le check n'est pas vert, ou si la PR modifie autre chose que `missions.json`.

Pour consulter le classement : ouvrez `leaderboard.json`, ou l'onglet **Actions** → workflow **Classement** (chaque exécution indique les points attribués).

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

Le `missions.json` livré **échoue volontairement** : il contient encore l'identifiant `TODO`. C'est le point de départ du jeu.
