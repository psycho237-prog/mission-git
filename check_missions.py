#!/usr/bin/env python3
"""Validateur du fichier missions.json pour l'atelier Mission Git.

Le script ne dépend d'aucune bibliothèque externe : il suffit de Python 3.
Il renvoie un code de sortie nul si le fichier est valide, non nul sinon.
"""

import json
import sys
from pathlib import Path

FICHIER_MISSIONS = Path(__file__).with_name("missions.json")
DIFFICULTES_AUTORISEES = (1, 2, 3)
NOMBRE_MINIMUM_DE_MISSIONS = 2
IDENTIFIANT_INTERDIT = "TODO"


def afficher_erreur(message):
    print("ERREUR : " + message, file=sys.stderr)


def charger_missions(chemin):
    """Lit et analyse le fichier JSON. Retourne (donnees, erreurs)."""
    if not chemin.is_file():
        return None, ["le fichier « {} » est absent.".format(chemin.name)]

    try:
        contenu = chemin.read_text(encoding="utf-8")
    except OSError as erreur:
        return None, [
            "impossible de lire « {} » ({}).".format(chemin.name, erreur)
        ]

    try:
        donnees = json.loads(contenu)
    except json.JSONDecodeError as erreur:
        return None, [
            "« {} » n'est pas un JSON valide : ligne {}, colonne {} ({})."
            .format(chemin.name, erreur.lineno, erreur.colno, erreur.msg)
        ]

    return donnees, []


def verifier_missions(donnees):
    """Applique les règles du jeu. Retourne la liste des erreurs."""
    erreurs = []

    if not isinstance(donnees, dict):
        return ["le contenu doit être un objet JSON avec une clé « missions »."]

    missions = donnees.get("missions")
    if not isinstance(missions, list):
        return ["la clé « missions » doit être une liste."]

    if len(missions) < NOMBRE_MINIMUM_DE_MISSIONS:
        erreurs.append(
            "il faut au moins {} missions, il y en a {}."
            .format(NOMBRE_MINIMUM_DE_MISSIONS, len(missions))
        )

    identifiants_vus = {}

    for position, mission in enumerate(missions, start=1):
        prefixe = "mission n° {}".format(position)

        if not isinstance(mission, dict):
            erreurs.append("{} : doit être un objet JSON.".format(prefixe))
            continue

        identifiant = mission.get("id")
        if not isinstance(identifiant, str) or not identifiant.strip():
            erreurs.append("{} : l'identifiant « id » doit être un texte non vide."
                           .format(prefixe))
        else:
            identifiant = identifiant.strip()

            if identifiant == IDENTIFIANT_INTERDIT:
                erreurs.append(
                    "{} : l'identifiant « {} » est interdit, remplacez-le par le nom de votre mission."
                    .format(prefixe, IDENTIFIANT_INTERDIT)
                )

            if identifiant in identifiants_vus:
                erreurs.append(
                    "{} : l'identifiant « {} » est déjà utilisé par la mission n° {}."
                    .format(prefixe, identifiant, identifiants_vus[identifiant])
                )
            else:
                identifiants_vus[identifiant] = position

        titre = mission.get("title")
        if not isinstance(titre, str) or not titre.strip():
            erreurs.append("{} : le titre « title » doit être un texte non vide."
                           .format(prefixe))

        difficulte = mission.get("difficulty")
        if isinstance(difficulte, bool) or not isinstance(difficulte, int):
            erreurs.append(
                "{} : la difficulté « difficulty » doit être un nombre entier (1, 2 ou 3)."
                .format(prefixe)
            )
        elif difficulte not in DIFFICULTES_AUTORISEES:
            erreurs.append(
                "{} : la difficulté vaut {}, elle doit valoir 1, 2 ou 3."
                .format(prefixe, difficulte)
            )

    return erreurs


def main():
    donnees, erreurs = charger_missions(FICHIER_MISSIONS)

    if donnees is not None:
        erreurs = verifier_missions(donnees)

    if erreurs:
        afficher_erreur("le fichier missions.json n'est pas conforme :")
        for erreur in erreurs:
            print("  - " + erreur, file=sys.stderr)
        print(
            "\nCorrigez missions.json puis relancez : python3 check_missions.py",
            file=sys.stderr,
        )
        return 1

    nombre = len(donnees["missions"])
    print("Bravo ! Les {} missions sont valides. L'équipe de secours peut partir."
          .format(nombre))
    return 0


if __name__ == "__main__":
    sys.exit(main())
