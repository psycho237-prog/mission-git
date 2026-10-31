# Mission Git

[Français](README.md) · **English**
À workshop game for learning pull requests, GitHub Actions checks and Git conflict resolution.

## The scenario

A rescue team must leave on a mission, but its mission board is incomplete. Each participant receives a **challenge card**: one precise mission to add to `missions.json`. Every card contains **one voluntary defect** that must be found and fixed before the robot (GitHub Actions) accepts the pull request (PR).

Because everyone replaces the same `TODO` block, Git eventually raises a **conflict** — that is the heart of the game.

## Participant journey

1. **Fork** the repository to your GitHub account (the *Fork* button).
2. **Create a branch** from the initial state of `main` in your fork:

   ```bash
   git clone https://github.com/<your-login>/mission-git.git
   cd mission-git
   git switch -c mission/<your-first-name>
   ```

3. **Discover your card** by opening a PR (even with no change) or, faster, locally:

   ```bash
   python3 check_missions.py --auteur <your-login>
   ```

   The output shows your login, your card, the mission to add (with its defect) and a hint.

4. **Replace the `TODO` block** with your card's mission, exactly as displayed.

5. **Open your PR** against `main` and **read the workflow result** in the *Checks* tab: it will be red, and that is expected.

6. **Merge `main` into your branch** as soon as GitHub reports a conflict (another participant merged first) and **resolve it**, keeping the other missions.

7. **Fix your card's defect** using the hints, then push:

   ```bash
   git add missions.json
   git commit -m "Corrige la mission de ma carte"
   git push
   ```

8. **Check** that the PR has no conflict left and that the workflow is **green**.

> Golden rule: only edit `missions.json`. Never touch `check_missions.py`, `cartes.json`, `update_leaderboard.py` or the workflows — the validator that runs comes from the base branch, and a PR touching those files is rejected in review.

## Your challenge card

### How it is assigned

Assignment is deterministic, with no randomness and no external service:

```
total = sum of the Unicode code points of the login characters, lowercased
card = cards[total % number_of_cards]
```

In other words: add the codes of your login's letters, divide by the number of cards and keep the remainder. **The same login always gets the same card.** The workflow uses the PR author's login (`github.event.pull_request.user.login`), so there is nothing to declare.

The available cards live in `cartes.json`: `colis-perdu`, `pont-effondre`, `radio-secours` and `avalanche`. Several people may receive the same card: their missions share the same title but have different identifiers (the login is part of the identifier), so everything stays compatible.

### The workflow message

On every run, the workflow shows:

- the **login** used for the assignment;
- the **card** assigned (identifier and title);
- the **mission to add**, with its voluntary defect;
- the **defect found** and a **hint** to fix it.

## Validation rules

The `check_missions.py` script verifies that:

- `missions.json` exists and contains valid JSON;
- the `missions` key is a list of **at least two missions**;
- each mission has a non-empty `id`, a non-empty `title` and an integer `difficulty` worth **1, 2 or 3**;
- the `TODO` identifier has been replaced;
- identifiers are **unique**;
- no mission already present on the base branch has been **deleted**: the workflow compares `missions.json` with the one from `main` (`--base`);
- **your card's mission** is present, with the expected identifier `<card>-<login>` and **no defect**.

As long as your card's defect remains, the check stays red even if the rest of the file is valid.

### Example of a corrected mission

For login `david`, the `colis-perdu` card gives:

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

Both missions are valid and the identifiers are unique.

## Progressive hints

Start with hint 1. Hint 2 is there if you get stuck.

| Defect | Hint 1 | Hint 2 |
| --- | --- | --- |
| Difficulty out of range | The `difficulty` field must be an integer, not text. | Only 1, 2 and 3 are accepted: replace 4 with 1, 2 or 3. |
| Empty title | A mission without a title cannot be shown to the rescue team. | Fill `title` with a short sentence describing the mission. |
| Empty identifier | Every mission needs an identifier to be found in the file. | Fill `id` with a unique text, for example `radio-secours-<your-login>`. |
| Duplicate identifier | Two missions cannot share the same identifier. | `demo` is already taken: choose another one, for example `avalanche-<your-login>`. |

Outside the faulty field, **change nothing**: the proposed identifier (`<card>-<login>`) must stay as is, unless the defect is precisely the identifier.

## Understanding the Git conflict

A conflict appears when two branches change **the same line** of the same file. Here, everyone replaces the same `TODO` block: Git cannot decide which version to keep and stops.

```bash
git fetch origin
git merge origin/main
```

Git then reports:

```
CONFLICT (content): Merge conflict in missions.json
Automatic merge failed; fix conflicts and then commit the result.
```

Open `missions.json`: Git has inserted markers.

```
<<<<<<< HEAD
      "id": "colis-perdu-david",
      ...
=======
      "id": "radio-secours-alice",
      ...
>>>>>>> origin/main
```

- `<<<<<<< HEAD` opens **your** version (your branch);
- `=======` separates the two versions;
- `>>>>>>> origin/main` closes the version coming from `main`.

You must **keep both missions** (yours and the others'), delete the three marker lines and check that the JSON commas and braces are still correct.

After resolving:

```bash
git add missions.json
git commit -m "Résout le conflit des missions"
git push
```

The check runs again automatically (`synchronize`): it must turn green.

## Workshop schedule (30 minutes)

| Time | Step |
| --- | --- |
| 0-3 min | Welcome, rescue team scenario, repository walkthrough. |
| 3-6 min | Demo: fork, branch, PR, reading the card message. |
| 6-14 min | Everyone forks, creates a branch, adds their card's mission and opens a PR. Checks are red: that is expected. |
| 14-17 min | The facilitator merges the first PR: the conflict appears for everyone else. |
| 17-25 min | Everyone merges `main`, resolves the conflict keeping all missions, fixes their card's defect and pushes. |
| 25-30 min | Merge the remaining PRs, leaderboard, wrap-up: PRs, checks, conflicts, good practices. |

## Automatic leaderboard

Every merged PR that passed the **Mission check** check awards **3 points** to its GitHub author. The leaderboard is written automatically to `leaderboard.json` by the **Classement** workflow.

### Scoring rules

- **3 points** per merged PR whose validation check is green at merge time.
- Existing scores are **preserved**: the file is extended, never reset.
- A PR is counted **only once**: its number is stored in `prs`, so re-running the workflow adds nothing.
- The leaderboard is **sorted by descending points**; ties are ordered alphabetically by login.
- A merged PR with no green check — or no check at all, for example from an unapproved fork — scores **0 points**: the workflow prints a warning, finishes green and changes nothing.
- Same for a PR that changes **anything other than `missions.json`** (validator, cards, workflows): it scores no points.

File format:

```json
{
  "entries": [
    { "login": "bob", "points": 6, "prs": [13, 14] },
    { "login": "alice", "points": 3, "prs": [12] }
  ]
}
```

### Viewing the leaderboard

- Open `leaderboard.json` in the repository: the list is current and already sorted.
- The **Actions** tab → **Classement** workflow: each run reports the points awarded and the PR author.
- The repository history shows the automated commits "Met à jour le classement (PR #12)".

## Checking the project locally

```bash
python3 check_missions.py --auteur <your-login>
python3 test_parcours.py
```

The shipped `missions.json` **fails on purpose**: it still contains the `TODO` identifier. That is the starting point of the game.

`test_parcours.py` replays the whole journey in a throwaway Git repository: red initial state, two participants' cards, conflict, resolution, refusal of a mission deletion and leaderboard. It touches neither the repository nor the network.

## Project structure

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

No external dependencies, no secrets, no deployment steps: Python 3 and Git are all you need.
