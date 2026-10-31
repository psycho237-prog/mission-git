# Guide d'installation de l'animateur

À faire **avant** de partager le dépôt : les participants doivent tous forker le
même état de `main`.

## 1. Vérifier le dépôt

```bash
python3 test_parcours.py      # doit afficher « Tout est vert »
python3 check_missions.py     # doit échouer : le bloc TODO est le point de départ
git status                    # doit être propre
```

- Remplacez le login de `.github/CODEOWNERS` par le vôtre (il est en `@psycho237-prog` par défaut).
- Poussez ce dépôt **avant** les forks : le workflow de validation est lu depuis la PR, il doit donc déjà exister sur `main`.

## 2. Réglages du dépôt (Settings)

**Actions → General**

- *Fork pull request workflows* : choisissez « Require approval for all outside collaborators ». Vous approuverez les runs dans l'onglet **Actions**.
- *Workflow permissions* : laissez « Read repository contents permission ». Les deux workflows déclarent leurs propres permissions (`contents: read` pour la validation, `contents: write` pour le classement), donc rien à élargir globalement.
- « Allow GitHub Actions to create and approve pull requests » : inutile, laissez décoché.

**Aucun secret n'est nécessaire.**

## 3. Protection de `main` (Settings → Branches)

Configuration retenue sur ce dépôt :

- [x] *Do not allow force pushes*
- [x] *Do not allow deletions*
- [ ] *Require a pull request before merging*
- [ ] *Require status checks to pass before merging*

Les deux dernières cases sont **volontairement décochées**, et ce n'est pas un oubli : le workflow **Classement** pousse un commit sur `main` avec le `GITHUB_TOKEN`, et sur un dépôt **personnel** le bot ne peut pas être autorisé à contourner la protection.

Test réalisé sur ce dépôt :

| Configuration | Poussée du bot sur `main` |
| --- | --- |
| Check obligatoire activé | **refusée** — `GH006: Protected branch update failed` / `Required status check "Vérifier les missions" is expected` |
| Check obligatoire retiré | **acceptée** |

L'API refuse aussi les autres portes de sortie sur un dépôt personnel :

- acteur de contournement « GitHub Actions » dans un ruleset → *« Actor GitHub Actions integration must be part of the ruleset source or owner organization »* ;
- restrictions de poussée (`restrictions`) → *« Only organization repositories can have users and team restrictions »*.

### Conséquences pratiques

- GitHub **ne bloque pas** la fusion d'une PR rouge : c'est à l'animateur de ne fusionner que les PR dont le check est vert.
- `.github/CODEOWNERS` reste **indicatif** : il sert de repère en revue, il ne bloque rien sans règle « Require a pull request ».
- ce qui protège réellement le jeu : les participants n'ont pas de droit d'écriture (fork obligatoire), le check exécute le validateur de la branche de base, et le classement refuse les points à toute PR qui touche autre chose que `missions.json`.

### Pour aller plus loin (facultatif)

- **Dépôt d'organisation** : l'app GitHub Actions devient un acteur de contournement valide, donc PR obligatoire + check obligatoire + revue Code Owners sont possibles.
- **Jeton personnel** : donner au workflow un `PAT` d'administrateur (secret `CLASSEMENT_TOKEN`) à la place de `secrets.GITHUB_TOKEN`. Le bot contourne alors la protection, mais le secret est à créer et à renouveler.

À éviter :

- *Require linear history* : les commits automatiques du classement seraient refusés.
- *Require signed commits* : les commits du bot ne sont pas signés.

## 4. Pendant l'atelier

1. Attendez que **toutes** les PR soient ouvertes avant d'en fusionner une seule (sinon pas de conflit).
2. Approuvez les runs de workflow venus des forks si GitHub les met en attente.
3. Fusionnez les PR une par une ; le workflow **Classement** met `leaderboard.json` à jour tout seul.
4. Une PR sans check vert rapporte 0 point : le job reste vert et affiche un avertissement `::warning::`, rien n'est écrit.

## 5. Dépannage

| Symptôme | Cause probable | Solution |
| --- | --- | --- |
| Le check n'apparaît jamais | Run de fork en attente d'approbation | Approuver dans **Actions** |
| Check rouge « TODO » | PR ouverte sans modification | Normal au début de l'exercice |
| Check rouge « mission supprimée » | Conflit résolu en effaçant les missions des autres | Fusionner `main` et garder toutes les missions |
| Workflow Classement en erreur `GH006: Protected branch update failed` | Un check obligatoire ou une PR obligatoire est actif sur `main` | Décocher la règle : le bot ne peut pas la contourner sur un dépôt personnel |
| 0 point alors que le check est vert | La PR touchait un autre fichier que `missions.json` | Normal : seul `missions.json` rapporte des points |
| Aucun conflit | PR fusionnées une par une | Repartir d'un état commun et ouvrir toutes les PR d'abord |
| Participants sans PR | Fork créé avant le dépôt de base | Leur faire re-forker, ou approuver leurs runs |
