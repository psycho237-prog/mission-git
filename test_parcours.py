#!/usr/bin/env python3
"""Rejoue le parcours de l'atelier dans un dépôt Git jetable.

Vérifie, sans réseau et sans GitHub :

- l'état de départ rouge (bloc `TODO`) ;
- la carte de chaque participant : défaut détecté, puis verte après correction ;
- le conflit Git quand deux branches remplacent le même bloc `TODO` ;
- le refus d'une PR qui supprime les missions déjà fusionnées (`--base`) ;
- le refus d'une PR qui remplace `check_missions.py` : le validateur exécuté
  est celui de la branche de base, appliqué au fichier de la PR ;
- le classement : 3 points par PR, une PR comptée une seule fois, tri stable.

Usage :

    python3 test_parcours.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent
FICHIERS = (
    "missions.json",
    "cartes.json",
    "check_missions.py",
    "update_leaderboard.py",
    "leaderboard.json",
)

CARTE_ALICE = {"id": "", "title": "Rétablir la radio de secours", "difficulty": 1}
CARTE_ALICE_OK = {"id": "radio-secours-alice", "title": "Rétablir la radio de secours", "difficulty": 1}
CARTE_BOB = {"id": "demo", "title": "Dégager une route bloquée par une avalanche", "difficulty": 2}
CARTE_BOB_OK = {"id": "avalanche-bob", "title": "Dégager une route bloquée par une avalanche", "difficulty": 2}
DEMO = {"id": "demo", "title": "Mission de démonstration", "difficulty": 1}

VERIFICATIONS = 0


def attendre(condition, description):
    """Échoue avec un message lisible si la condition est fausse."""
    global VERIFICATIONS
    if not condition:
        raise AssertionError(description)
    VERIFICATIONS += 1
    print("  ok  " + description)


def executer(depot, *commande, succes=True):
    resultat = subprocess.run(
        list(commande), cwd=depot, text=True, capture_output=True, env=dict(os.environ)
    )
    if succes and resultat.returncode != 0:
        raise AssertionError(
            "échec de « {} » (code {}) :\n{}{}".format(
                " ".join(commande), resultat.returncode, resultat.stdout, resultat.stderr
            )
        )
    return resultat


def git(depot, *arguments, succes=True):
    return executer(depot, "git", *arguments, succes=succes)


def verifier(depot, *options):
    """Lance check_missions.py et retourne (code, sortie combinée)."""
    resultat = executer(
        depot, sys.executable, "check_missions.py", *options, succes=False
    )
    return resultat.returncode, resultat.stdout + resultat.stderr


def ecrire_missions(depot, missions):
    chemin = Path(depot, "missions.json")
    chemin.write_text(
        json.dumps({"missions": missions}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def initialiser(dossier):
    depot = dossier / "mission-git"
    depot.mkdir()
    for nom in FICHIERS:
        shutil.copy2(RACINE / nom, depot / nom)
    git(depot, "init", "-q", "-b", "main")
    git(depot, "config", "user.name", "Test")
    git(depot, "config", "user.email", "test@example.com")
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "État initial")
    return depot


def tester_depart(depot):
    print("\n1. État de départ (bloc TODO)")
    code, sortie = verifier(depot)
    attendre(code == 1, "le fichier livré échoue volontairement")
    attendre("TODO" in sortie, "le message cite l'identifiant TODO interdit")

    code, sortie = verifier(depot, "--auteur", "alice")
    attendre(code == 1, "le check est rouge pour alice sans aucune modification")
    attendre("radio-secours" in sortie, "la carte d'alice est affichée")


def tester_carte(depot, pseudo, carte, carte_corrigee, message_defaut):
    print("\n2. Carte de {} : défaut puis correction".format(pseudo))
    git(depot, "switch", "-q", "-c", "mission/{}".format(pseudo), "main")
    ecrire_missions(depot, [DEMO, carte])
    git(depot, "commit", "-q", "-am", "Ajoute la mission de ma carte")

    code, sortie = verifier(depot, "--auteur", pseudo)
    attendre(code == 1, "le check reste rouge avec le défaut de la carte")
    attendre(message_defaut in sortie, "le défaut est identifié : « {} »".format(message_defaut))

    ecrire_missions(depot, [DEMO, carte_corrigee])
    git(depot, "commit", "-q", "-am", "Corrige la mission de ma carte")
    code, sortie = verifier(depot, "--auteur", pseudo)
    attendre(code == 0, "le check passe au vert après correction")
    attendre("Aucun défaut détecté" in sortie, "le message confirme l'absence de défaut")


def tester_conflit(depot, dossier):
    print("\n3. Fusion des PR et conflit Git")
    git(depot, "switch", "-q", "main")
    git(depot, "merge", "-q", "--no-edit", "mission/alice")
    code, _ = verifier(depot, "--auteur", "alice")
    attendre(code == 0, "la première PR fusionnée est valide")

    resultat = git(depot, "merge", "mission/bob", succes=False)
    attendre(resultat.returncode != 0, "la fusion suivante provoque un conflit")
    attendre("CONFLICT" in resultat.stdout + resultat.stderr, "Git annonce CONFLICT")
    statut = git(depot, "status", "--porcelain").stdout
    attendre("UU missions.json" in statut, "missions.json est bien en conflit")
    contenu = Path(depot, "missions.json").read_text(encoding="utf-8")
    attendre("<<<<<<<" in contenu and ">>>>>>>" in contenu, "les marqueurs de conflit sont présents")

    ecrire_missions(depot, [DEMO, CARTE_ALICE_OK, CARTE_BOB_OK])
    git(depot, "add", "missions.json")
    git(depot, "commit", "-q", "--no-edit")
    for pseudo in ("alice", "bob"):
        code, _ = verifier(depot, "--auteur", pseudo)
        attendre(code == 0, "après résolution, le check est vert pour {}".format(pseudo))

    base = dossier / "base.json"
    shutil.copy2(Path(depot, "missions.json"), base)
    return base


def tester_suppression(depot, base):
    print("\n4. Une PR ne peut pas supprimer les missions des autres")
    git(depot, "switch", "-q", "-c", "mission/triche")
    ecrire_missions(depot, [DEMO, CARTE_ALICE_OK])
    git(depot, "commit", "-q", "-am", "Supprime les missions des autres")

    code, _ = verifier(depot, "--auteur", "alice")
    attendre(code == 0, "sans référence de base, le fichier seul paraît valide")

    code, sortie = verifier(depot, "--auteur", "alice", "--base", str(base))
    attendre(code == 1, "avec --base, la suppression est refusée")
    attendre("avalanche-bob" in sortie, "le message nomme la mission supprimée")
    attendre("supprimée" in sortie, "le message explique la règle")

    git(depot, "switch", "-q", "main")
    git(depot, "branch", "-q", "-D", "mission/triche")


def tester_falsification(depot, dossier):
    print("\n5. Une PR ne peut pas remplacer le validateur")
    git(depot, "switch", "-q", "-c", "mission/mallory")
    Path(depot, "check_missions.py").write_text(
        'print("Bravo ! Les missions sont valides.")\nraise SystemExit(0)\n',
        encoding="utf-8",
    )
    ecrire_missions(depot, [DEMO])
    git(depot, "commit", "-q", "-am", "Remplace le validateur")

    code, _ = verifier(depot, "--auteur", "mallory")
    attendre(code == 0, "le validateur réécrit par la PR se déclare vert")

    validateur = dossier / "validateur-base"
    validateur.mkdir()
    for nom in ("check_missions.py", "cartes.json", "missions.json"):
        contenu = git(depot, "show", "main:{}".format(nom)).stdout
        (validateur / nom).write_text(contenu, encoding="utf-8")

    resultat = executer(
        dossier,
        sys.executable,
        str(validateur / "check_missions.py"),
        "--auteur",
        "mallory",
        "--missions",
        str(Path(depot, "missions.json")),
        "--base",
        str(validateur / "missions.json"),
        succes=False,
    )
    sortie = resultat.stdout + resultat.stderr
    attendre(resultat.returncode == 1, "le validateur de la branche de base refuse la PR")
    attendre("au moins 2 missions" in sortie, "le refus est explicite")

    git(depot, "switch", "-q", "main")


def tester_classement(depot):
    print("\n6. Classement automatique")
    for login, numero in (("alice", 12), ("bob", 13), ("carol", 14)):
        executer(
            depot,
            sys.executable,
            "update_leaderboard.py",
            "--login",
            login,
            "--pr",
            str(numero),
            "--points",
            "3",
        )

    sortie = executer(
        depot,
        sys.executable,
        "update_leaderboard.py",
        "--login",
        "bob",
        "--pr",
        "13",
        "--points",
        "3",
    ).stdout
    attendre("déjà rapporté" in sortie, "rejouer une PR ne rajoute aucun point")

    classement = json.loads(Path(depot, "leaderboard.json").read_text(encoding="utf-8"))
    entrees = classement["entries"]
    attendre(len(entrees) == 3, "trois participants sont classés")
    attendre(all(e["points"] == 3 for e in entrees), "chacun a 3 points")
    attendre(
        [e["login"] for e in entrees] == ["alice", "bob", "carol"],
        "à égalité, l'ordre alphabétique est respecté",
    )
    attendre(entrees[0]["prs"] == [12], "le numéro de PR est enregistré")


def main():
    dossier = Path(tempfile.mkdtemp(prefix="mission-git-test-"))
    try:
        depot = initialiser(dossier)
        tester_depart(depot)
        tester_carte(
            depot, "alice", CARTE_ALICE, CARTE_ALICE_OK,
            "l'identifiant de votre mission est vide",
        )
        tester_carte(
            depot, "bob", CARTE_BOB, CARTE_BOB_OK,
            "l'identifiant de votre mission est déjà utilisé",
        )
        base = tester_conflit(depot, dossier)
        tester_suppression(depot, base)
        tester_falsification(depot, dossier)
        tester_classement(depot)
    except AssertionError as erreur:
        print("\nÉCHEC : {}".format(erreur), file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(dossier, ignore_errors=True)

    print("\nTout est vert : {} vérifications.".format(VERIFICATIONS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
