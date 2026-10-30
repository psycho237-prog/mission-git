#!/usr/bin/env python3
"""Validateur de missions.json pour l'atelier Mission Git.

Deux niveaux de vérification :

1. les règles générales du fichier (JSON, nombre de missions, champs valides,
   identifiants uniques, pas de `TODO`) ;
2. la carte de défi attribuée à l'auteur de la pull request, choisie de façon
   déterministe à partir de son pseudo GitHub.

Attribution des cartes (sans hasard, sans service externe) :

    total = somme des codes Unicode des caractères du pseudo, en minuscules
    carte = cartes[total % nombre_de_cartes]

Aucune bibliothèque externe n'est nécessaire. Exemple :

    python3 check_missions.py --auteur alice
"""

import argparse
import json
import sys
from pathlib import Path

FICHIER_MISSIONS = Path(__file__).with_name("missions.json")
FICHIER_CARTES = Path(__file__).with_name("cartes.json")

DIFFICULTES_AUTORISEES = (1, 2, 3)
NOMBRE_MINIMUM_DE_MISSIONS = 2
IDENTIFIANT_INTERDIT = "TODO"
IDENTIFIANT_DEMO = "demo"

DEF_AUTRE = "autre"
DEF_DIFFICULTE = "difficulte_hors_limites"
DEF_TITRE = "titre_vide"
DEF_IDENTIFIANT = "identifiant_vide"
DEF_DOUBLON = "identifiant_duplique"

LIBELLES_DEFAUTS = {
    DEF_DIFFICULTE: "la difficulté de votre mission ne vaut pas 1, 2 ou 3.",
    DEF_TITRE: "le titre de votre mission est vide.",
    DEF_IDENTIFIANT: "l'identifiant de votre mission est vide.",
    DEF_DOUBLON: "l'identifiant de votre mission est déjà utilisé par une autre mission.",
}


def normaliser(texte):
    """Compare les textes sans tenir compte de la casse ni des espaces superflus."""
    return " ".join(texte.split()).casefold()


def charger_json(chemin):
    """Lit et analyse un fichier JSON. Retourne (donnees, erreurs)."""
    if not chemin.is_file():
        return None, ["le fichier « {} » est absent.".format(chemin.name)]

    try:
        contenu = chemin.read_text(encoding="utf-8")
    except OSError as erreur:
        return None, ["impossible de lire « {} » ({}).".format(chemin.name, erreur)]

    try:
        return json.loads(contenu), []
    except json.JSONDecodeError as erreur:
        return None, [
            "« {} » n'est pas un JSON valide : ligne {}, colonne {} ({})."
            .format(chemin.name, erreur.lineno, erreur.colno, erreur.msg)
        ]


def charger_cartes():
    """Charge cartes.json et vérifie sa structure. Retourne (donnees, erreurs)."""
    donnees, erreurs = charger_json(FICHIER_CARTES)
    if erreurs:
        return None, erreurs

    if not isinstance(donnees, dict) or not isinstance(donnees.get("cartes"), list):
        return None, ["« cartes.json » doit contenir une liste « cartes »."]

    if not donnees["cartes"]:
        return None, ["« cartes.json » ne contient aucune carte."]

    for position, carte in enumerate(donnees["cartes"], start=1):
        prefixe = "carte n° {}".format(position)
        if not isinstance(carte, dict):
            return None, ["{} : doit être un objet JSON.".format(prefixe)]
        for cle in ("id", "titre", "defaut"):
            if not isinstance(carte.get(cle), str) or not carte[cle].strip():
                return None, ["{} : la clé « {} » doit être un texte non vide."
                              .format(prefixe, cle)]
        if isinstance(carte.get("difficulte"), bool) or not isinstance(
            carte.get("difficulte"), int
        ):
            return None, ["{} : la clé « difficulte » doit être un entier."
                          .format(prefixe)]

    indices = donnees.setdefault("indices", {})
    if not isinstance(indices, dict):
        return None, ["« cartes.json » : la clé « indices » doit être un objet."]

    return donnees, []


def choisir_carte(pseudo, cartes):
    """Sélection déterministe : somme des codes Unicode modulo le nombre de cartes."""
    total = sum(ord(caractere) for caractere in pseudo.casefold())
    return cartes[total % len(cartes)]


def identifiant_attendu(carte, pseudo):
    return "{}-{}".format(carte["id"], pseudo.casefold())


def mission_de_depart(carte, pseudo):
    """Reconstruit la mission de la carte telle qu'elle est proposée, défaut compris."""
    mission = {
        "id": identifiant_attendu(carte, pseudo),
        "title": carte["titre"],
        "difficulty": carte["difficulte"],
    }
    defaut = carte["defaut"]
    if defaut == DEF_DIFFICULTE:
        mission["difficulty"] = 4
    elif defaut == DEF_TITRE:
        mission["title"] = ""
    elif defaut == DEF_IDENTIFIANT:
        mission["id"] = ""
    elif defaut == DEF_DOUBLON:
        mission["id"] = IDENTIFIANT_DEMO
    return mission


def detecter_defauts(mission, missions):
    """Liste les défauts d'une mission, dans l'ordre : id, titre, difficulté."""
    defauts = []

    identifiant = mission.get("id")
    if not isinstance(identifiant, str) or not identifiant.strip():
        defauts.append(DEF_IDENTIFIANT)
    else:
        identifiant = identifiant.strip()
        occurrences = sum(
            1
            for autre in missions
            if isinstance(autre, dict)
            and isinstance(autre.get("id"), str)
            and autre["id"].strip() == identifiant
        )
        if occurrences > 1:
            defauts.append(DEF_DOUBLON)

    titre = mission.get("title")
    if not isinstance(titre, str) or not titre.strip():
        defauts.append(DEF_TITRE)

    difficulte = mission.get("difficulty")
    if isinstance(difficulte, bool) or not isinstance(difficulte, int) or (
        difficulte not in DIFFICULTES_AUTORISEES
    ):
        defauts.append(DEF_DIFFICULTE)

    return defauts


def verifier_carte(missions, carte, pseudo):
    """Retourne (mission_de_la_carte, problemes).

    problemes contient des codes de défaut, ou « absente » / « identifiant_inattendu ».
    """
    attendu = identifiant_attendu(carte, pseudo)

    nommees = [
        mission
        for mission in missions
        if isinstance(mission, dict)
        and isinstance(mission.get("id"), str)
        and mission["id"].strip() == attendu
    ]
    if nommees:
        return nommees[0], detecter_defauts(nommees[0], missions)

    titre = normaliser(carte["titre"])
    memes_titres = [
        mission
        for mission in missions
        if isinstance(mission, dict)
        and isinstance(mission.get("title"), str)
        and normaliser(mission["title"]) == titre
    ]

    defectueuses = [
        (mission, detecter_defauts(mission, missions)) for mission in memes_titres
    ]
    defectueuses = [paire for paire in defectueuses if paire[1]]
    if defectueuses:
        return defectueuses[0]

    if memes_titres:
        return None, ["identifiant_inattendu"]

    return None, ["absente"]


def verifier_missions(donnees, ignorer=None):
    """Applique les règles générales. Retourne la liste des erreurs."""
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
        if mission is ignorer:
            continue

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
                    "{} : l'identifiant « {} » est interdit, remplacez-le par la mission de votre carte."
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


def afficher_problemes_carte(problemes, carte, pseudo, indices):
    attendu = identifiant_attendu(carte, pseudo)

    if "absente" in problemes:
        print("La mission de votre carte est absente de missions.json.")
        print("Copiez le bloc ci-dessus à la place du bloc TODO, puis poussez.")
        print("Identifiant attendu pour votre mission : « {} ».".format(attendu))
        return

    if "identifiant_inattendu" in problemes:
        print("Votre mission porte un identifiant inattendu.")
        print("Identifiant attendu : « {} ».".format(attendu))
        return

    for defaut in problemes:
        libelle = LIBELLES_DEFAUTS.get(defaut)
        if libelle is None:
            continue
        print("DÉFAUT TROUVÉ : {}".format(libelle))
        conseils = indices.get(defaut) or []
        if conseils:
            print("INDICE : {}".format(conseils[0].replace("<pseudo>", pseudo.casefold())))
        if len(conseils) > 1:
            print("Un indice plus précis se trouve dans le README (section « Indices progressifs »).")
        print("")


def main(argv=None):
    analyseur = argparse.ArgumentParser(
        description="Vérifie missions.json et la carte de défi de l'auteur de la PR."
    )
    analyseur.add_argument(
        "--auteur",
        default="",
        help="pseudo GitHub de l'auteur de la PR (attribue la carte de défi)",
    )
    analyseur.add_argument(
        "--missions",
        type=Path,
        default=FICHIER_MISSIONS,
        help="chemin de missions.json (utilisé pour les tests)",
    )
    options = analyseur.parse_args(argv)

    pseudo = options.auteur.strip()
    carte = None
    indices = {}

    if pseudo:
        donnees_cartes, erreurs_cartes = charger_cartes()
        if erreurs_cartes:
            print("ERREUR : les cartes de défi sont illisibles :", file=sys.stderr)
            for erreur in erreurs_cartes:
                print("  - " + erreur, file=sys.stderr)
            return 1
        cartes = donnees_cartes["cartes"]
        carte = choisir_carte(pseudo, cartes)
        indices = donnees_cartes["indices"]

        print("=== Votre carte de défi ===")
        print("Pseudo utilisé pour l'attribution : {}".format(pseudo))
        print("Carte attribuée : {} — {}".format(carte["id"], carte["titre"]))
        print(
            "Attribution : somme des codes des lettres du pseudo, modulo {} "
            "(pas de hasard, même pseudo = même carte).".format(len(cartes))
        )
        print("Mission à ajouter à la place du bloc TODO :")
        print(json.dumps(mission_de_depart(carte, pseudo), ensure_ascii=False, indent=2))
        print("Ce bloc contient un défaut volontaire : à vous de le repérer et de le corriger.")
        print("")

    donnees, erreurs = charger_json(options.missions)
    if donnees is None:
        print("ERREUR : {}".format(erreurs[0]), file=sys.stderr)
        return 1

    missions = donnees.get("missions") if isinstance(donnees, dict) else None

    mission_carte = None
    problemes_carte = []
    if carte is not None and isinstance(missions, list):
        mission_carte, problemes_carte = verifier_carte(missions, carte, pseudo)
        if problemes_carte:
            afficher_problemes_carte(problemes_carte, carte, pseudo, indices)
        else:
            print("Aucun défaut détecté sur la mission de votre carte.")
            print("")

    erreurs_globales = verifier_missions(donnees, ignorer=mission_carte)

    if erreurs_globales:
        print("ERREUR : le fichier missions.json n'est pas conforme :", file=sys.stderr)
        for erreur in erreurs_globales:
            print("  - " + erreur, file=sys.stderr)
        print(
            "\nCorrigez missions.json puis poussez à nouveau sur votre branche.",
            file=sys.stderr,
        )
        return 1

    if problemes_carte:
        print("La carte n'est pas encore corrigée : le check reste rouge.", file=sys.stderr)
        return 1

    if carte is None:
        print(
            "Pseudo non fourni : vérification générale seulement. "
            "Le workflow, lui, utilise le pseudo de l'auteur de la PR."
        )

    nombre = len(missions)
    if carte is not None:
        print(
            "Bravo ! Les {} missions sont valides et la carte « {} » de {} est corrigée."
            .format(nombre, carte["id"], pseudo)
        )
    else:
        print(
            "Bravo ! Les {} missions sont valides. L'équipe de secours peut partir."
            .format(nombre)
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
