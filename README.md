# Mission Git

Mini-jeu d'atelier pour apprendre les pull requests, les checks GitHub Actions et la résolution de conflits Git.

## Le scénario

Une équipe de secours doit partir en mission, mais son tableau de missions est incomplet. Votre équipe doit **ajouter une mission** dans `missions.json` pour que le départ soit autorisé.

Chaque participant travaille sur sa propre branche et ouvre sa propre pull request (PR). Un robot (GitHub Actions) vérifie automatiquement le fichier à chaque PR. Quand plusieurs personnes modifient le même endroit du fichier, Git provoque un **conflit** : c'est le cœur du jeu.

## Les règles de validation

Le script `check_missions.py` vérifie que :

- `missions.json` existe et contient du JSON valide ;
- la clé `missions` est une liste d'**au moins deux missions** ;
- chaque mission possède un `id` non vide, un `title` non vide et une `difficulty` entière valant **1, 2 ou 3** ;
- l'identifiant `TODO` est interdit (il faut le remplacer par le nom de votre mission) ;
- les identifiants sont **uniques**.

Au moindre écart, le script affiche les erreurs en français et renvoie un code de sortie non nul. Le check GitHub Actions passe alors au rouge.

### Condition de victoire

Votre PR est gagnante quand :

1. le check **Mission check** est vert ;
2. votre mission est bien présente dans `missions.json` ;
3. votre branche est à jour avec `main` (conflit résolu et correctif poussé).

L'atelier est réussi lorsque toutes les PR de l'équipe sont vertes et fusionnées.

## Exemple de mission valide

```json
{
  "missions": [
    {
      "id": "demo",
      "title": "Mission de démonstration",
      "difficulty": 1
    },
    {
      "id": "sauvetage-montagne",
      "title": "Secourir deux randonneurs bloqués par la neige",
      "difficulty": 3
    }
  ]
}
```

Dans cet exemple, le `TODO` a été remplacé par une vraie mission : l'identifiant `sauvetage-montagne` est unique, le titre est explicite et la difficulté vaut 3.

## Mettre en place l'atelier (animateur)

1. Créer le dépôt sur GitHub à partir de ce dossier.
2. Vérifier que l'onglet **Actions** est activé.
3. S'assurer que tout le monde part du même état de `main`.

## Le parcours d'un participant

### 1. Créer sa branche depuis le même état de `main`

```bash
git clone <url-du-depot>
cd mission-git
git switch -c mission/<votre-prenom>
```

### 2. Modifier `missions.json`

Remplacez le bloc `TODO` par votre propre mission (identifiant unique, titre clair, difficulté 1 à 3).

### 3. Vérifier en local avant de pousser

```bash
python3 check_missions.py
```

Le message `Bravo ! Les 2 missions sont valides.` (ou plus) indique que tout est bon.

### 4. Committer et pousser

```bash
git add missions.json
git commit -m "Ajoute la mission <nom>"
git push -u origin mission/<votre-prenom>
```

### 5. Ouvrir la pull request

- Sur GitHub, cliquez sur **Compare & pull request**.
- Titre suggéré : `Mission : <nom de la mission>`.
- Ouvrez la PR **vers `main`**.

### 6. Consulter le résultat du workflow

- Onglet **Checks** de la PR, ou onglet **Actions** du dépôt.
- Vert = tout est bon. Rouge = cliquez sur le job **Vérifier les missions** pour lire l'erreur affichée par le script.

## Résoudre le conflit (le moment fort du jeu)

Quand le premier participant a fusionné sa PR, mettez votre branche à jour :

```bash
git fetch origin
git merge origin/main
```

Git signale alors un conflit sur `missions.json` :

```
CONFLICT (content): Merge conflict in missions.json
Automatic merge failed; fix conflicts and then commit the result.
```

### Comprendre les marqueurs de conflit

Ouvrez `missions.json` : Git a inséré des marqueurs dans le bloc concerné.

```
<<<<<<< HEAD
      "id": "votre-mission",
      "title": "Votre titre",
=======
      "id": "mission-du-voisin",
      "title": "Le titre du voisin",
>>>>>>> origin/main
```

- `<<<<<<< HEAD` ouvre **votre** version (la branche courante) ;
- `=======` sépare les deux versions ;
- `>>>>>>> origin/main` ferme la version venant de `main`.

Vous devez **choisir, fusionner ou réécrire** le bloc, puis **supprimer les trois lignes de marqueurs**. Le fichier final doit rester du JSON valide, avec les deux missions conservées et des identifiants uniques.

### Enregistrer le correctif

Après résolution :

```bash
git add missions.json
git commit -m "Résout le conflit des missions"
git push
```

Le check se relance automatiquement sur la PR (`synchronize`) : il doit repasser au vert.

## Déroulé de l'atelier (30 minutes)

| Durée | Étape |
| --- | --- |
| 0-3 min | Accueil, scénario de l'équipe de secours, présentation du dépôt. |
| 3-8 min | Démonstration : branche, modification, PR, check vert. |
| 8-15 min | Les participants créent leur branche, modifient `missions.json` et ouvrent leur PR. |
| 15-18 min | L'animateur fusionne la première PR : le conflit apparaît chez les autres. |
| 18-26 min | Chacun met à jour `main`, résout le conflit, pousse le correctif et voit son check repasser au vert. |
| 26-30 min | Fusion des PR restantes, bilan : PR, checks, conflits, bonnes pratiques. |

## Consigne d'animation (indispensable)

> **Tous les participants doivent créer leur branche depuis le même état de `main` et ouvrir leur PR avant la fusion de la première PR.**

C'est cette simultanéité qui provoque le conflit pédagogique. Si les PR sont ouvertes et fusionnées une par une, le conflit n'apparaît pas et l'exercice perd son intérêt. Surveillez donc l'ouverture des PR et ne fusionnez la première qu'une fois que tout le monde a la sienne.

## Option de secours si le conflit n'apparaît pas

Demandez à **deux participants de modifier exactement le même bloc `TODO`**, au même endroit du fichier, avec des identifiants différents. Le conflit est alors garanti, même si le reste du fichier diffère.

Autre dépannage : vérifiez que les participants ont bien fait `git fetch origin` puis `git merge origin/main` (et non `git pull` sur une branche jamais liée).

## Avertissement pratique : les PR venant de forks

Les checks GitHub Actions sur une PR ouverte depuis un **fork** peuvent dépendre des réglages du dépôt :

- pour les contributeurs externes, GitHub peut exiger une **approbation manuelle** avant de lancer le workflow ;
- les secrets ne sont pas transmis aux workflows déclenchés par un fork ;
- selon la configuration du dépôt, le workflow peut ne pas se lancer du tout.

Pour un atelier sans surprise, le plus simple est que les participants soient **collaborateurs du dépôt** et poussent leurs branches directement dans le dépôt (pas depuis un fork). Sinon, prévoyez d'approuver les runs manuellement dans l'onglet **Actions**.

## Vérifier le projet en local

```bash
python3 check_missions.py
```

Le fichier `missions.json` livré **échoue volontairement** : il contient encore l'identifiant `TODO`. C'est le point de départ du jeu. Le script affiche une erreur et renvoie un code de sortie non nul.

## Structure du projet

```
mission-git/
├── README.md
├── missions.json
├── check_missions.py
└── .github/
    └── workflows/
        └── mission-check.yml
```

Aucune dépendance externe, aucun secret, aucun déploiement : Python 3 et Git suffisent.
