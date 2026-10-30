#!/usr/bin/env python3
"""Met à jour le classement (leaderboard.json) après la fusion d'une PR.

Appelé par le workflow « Classement », jamais par celui qui valide les PR.
Le script ne dépend d'aucune bibliothèque externe et n'accède pas au réseau.

Exemple :
    python3 update_leaderboard.py --login alice --pr 12 --points 3
"""

import argparse
import json
import sys
from pathlib import Path

FICHIER_CLASSEMENT = Path(__file__).with_name("leaderboard.json")


def afficher_erreur(message):
    print("ERREUR : " + message, file=sys.stderr)


def charger_classement(chemin):
    """Lit leaderboard.json. Retourne (donnees, erreurs)."""
    if not chemin.is_file():
        return None, ["le fichier « {} » est absent.".format(chemin.name)]

    try:
        contenu = chemin.read_text(encoding="utf-8")
    except OSError as erreur:
        return None, ["impossible de lire « {} » ({}).".format(chemin.name, erreur)]

    try:
        donnees = json.loads(contenu)
    except json.JSONDecodeError as erreur:
        return None, [
            "« {} » n'est pas un JSON valide : ligne {}, colonne {} ({})."
            .format(chemin.name, erreur.lineno, erreur.colno, erreur.msg)
        ]

    if not isinstance(donnees, dict):
        return None, ["le contenu doit être un objet JSON avec une clé « entries »."]

    entrees = donnees.get("entries")
    if not isinstance(entrees, list):
        return None, ["la clé « entries » doit être une liste."]

    erreurs = []
    for position, entree in enumerate(entrees, start=1):
        prefixe = "entrée n° {}".format(position)
        if not isinstance(entree, dict):
            erreurs.append("{} : doit être un objet JSON.".format(prefixe))
            continue
        if not isinstance(entree.get("login"), str) or not entree["login"].strip():
            erreurs.append("{} : le « login » doit être un texte non vide.".format(prefixe))
        points = entree.get("points")
        if isinstance(points, bool) or not isinstance(points, int) or points < 0:
            erreurs.append("{} : « points » doit être un entier positif ou nul.".format(prefixe))
        prs = entree.get("prs")
        if not isinstance(prs, list) or any(
            isinstance(numero, bool) or not isinstance(numero, int) for numero in prs
        ):
            erreurs.append("{} : « prs » doit être une liste de numéros de PR.".format(prefixe))

    if erreurs:
        return None, erreurs
    return donnees, []


def pr_deja_comptee(entrees, numero):
    """Retourne le login qui a déjà reçu les points de cette PR, sinon None."""
    for entree in entrees:
        if numero in entree["prs"]:
            return entree["login"]
    return None


def enregistrer_classement(chemin, donnees):
    chemin.write_text(
        json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def construire_analyseur():
    analyseur = argparse.ArgumentParser(
        description="Ajoute les points d'une PR fusionnée au classement."
    )
    analyseur.add_argument("--login", required=True, help="auteur GitHub de la PR")
    analyseur.add_argument("--pr", required=True, type=int, help="numéro de la PR")
    analyseur.add_argument(
        "--points", type=int, default=3, help="points attribués (3 par défaut)"
    )
    analyseur.add_argument(
        "--fichier",
        type=Path,
        default=FICHIER_CLASSEMENT,
        help="chemin du classement (leaderboard.json par défaut)",
    )
    return analyseur


def main(argv=None):
    options = construire_analyseur().parse_args(argv)

    login = options.login.strip()
    if not login:
        afficher_erreur("le login GitHub de l'auteur est vide.")
        return 1
    if options.pr <= 0:
        afficher_erreur("le numéro de PR doit être un entier positif.")
        return 1
    if options.points <= 0:
        afficher_erreur("le nombre de points doit être un entier positif.")
        return 1

    donnees, erreurs = charger_classement(options.fichier)
    if erreurs:
        afficher_erreur("le classement n'est pas exploitable :")
        for erreur in erreurs:
            print("  - " + erreur, file=sys.stderr)
        return 1

    entrees = donnees["entries"]

    deja_comptee = pr_deja_comptee(entrees, options.pr)
    if deja_comptee is not None:
        print(
            "La PR #{} a déjà rapporté ses points à {} : aucun changement."
            .format(options.pr, deja_comptee)
        )
        return 0

    entree = next((e for e in entrees if e["login"] == login), None)
    if entree is None:
        entree = {"login": login, "points": 0, "prs": []}
        entrees.append(entree)

    entree["points"] += options.points
    entree["prs"].append(options.pr)
    entree["prs"].sort()

    # Tri : points décroissants, puis login alphabétique pour départager.
    entrees.sort(key=lambda e: (-e["points"], e["login"].lower()))
    donnees["entries"] = entrees

    enregistrer_classement(options.fichier, donnees)
    print(
        "{} points attribués à {} pour la PR #{} (total : {} points)."
        .format(options.points, login, options.pr, entree["points"])
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
