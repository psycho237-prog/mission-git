# Mission Git

[Français](README.md) · **English**

A workshop mini-game for learning pull requests, GitHub Actions checks and Git conflict resolution.

## The scenario

A rescue team must leave on a mission, but its mission board is incomplete. Each participant receives a **challenge card**: one precise mission to add to `missions.json`, with **one voluntary defect** to fix before the verification robot (GitHub Actions) accepts the pull request (PR).

Because everyone replaces the same `TODO` block, Git eventually raises a **conflict**: that is the heart of the game.

## The journey in 6 steps

### 1. Fork, clone, create a branch

Click **Fork**, then:

```bash
git clone https://github.com/<your-login>/mission-git.git
cd mission-git
git switch -c mission/<your-first-name>
```

### 2. Find your card

Using your GitHub login:

```bash
python3 check_missions.py --auteur <your-login>
```

The output shows your card, the mission to add **with its defect**, and a hint.

### 3. Replace the `TODO` block

In `missions.json`, replace the `TODO` mission with the one displayed, **without fixing it yet**. The robot will reject it: that is intended.

### 4. Push and open the PR

```bash
git add missions.json
git commit -m "Ajoute la mission de ma carte"
git push -u origin mission/<your-first-name>
```

Then open the PR against `main` of the original repository. In the *Checks* tab, the **Vérifier les missions** check is **red**: your card's defect is still there.

### 5. Bring in `main` and resolve the conflict

As soon as another participant has merged, GitHub reports a conflict on your PR.

On your fork page, click **Sync fork → Update branch**, then:

```bash
git pull origin main
```

Without the button, add the original repository as a remote:

```bash
git remote add upstream https://github.com/<owner>/mission-git.git
git fetch upstream
git merge upstream/main
```

Git stops on a conflict in `missions.json`. The [Resolving the Git conflict](#resolving-the-git-conflict) section explains what to do: keep **all** missions.

### 6. Fix the defect, push, check

Fix the faulty field using the [hints](#progressive-hints), then:

```bash
python3 check_missions.py --auteur <your-login>   # must be green before pushing
git add missions.json
git commit -m "Corrige la mission de ma carte"
git push
```

The check runs again by itself: it must be **green** and the PR conflict-free.

> **Golden rule:** only edit `missions.json`. It is the only file expected in your PR.

## Your challenge card

Your card depends on your GitHub login: **the same login always gets the same card**, there is nothing to declare. The workflow reads the PR author and shows the expected mission, its identifier (`<card>-<login>`) and a hint.

Several participants may receive the same card: the login is part of the identifier, so the missions stay different.

## Validation rules

`missions.json` must follow these rules:

- valid JSON, with a `missions` key holding **at least two missions**;
- for each mission: a non-empty, **unique** `id`, a non-empty `title`, and an integer `difficulty` worth **1, 2 or 3**;
- the `TODO` block replaced;
- no mission already present on `main` **deleted**: keep the other missions;
- **your** mission present, with the identifier `<card>-<login>` and **no defect**.

As long as your card's defect remains, the check stays red.

### Example of a corrected mission

Login `david`, card `colis-perdu`:

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

## Progressive hints

Start with hint 1. Hint 2 is there if you get stuck.

| Defect | Hint 1 | Hint 2 |
| --- | --- | --- |
| Difficulty out of range | The `difficulty` field must be an integer, not text. | Only 1, 2 and 3 are accepted: replace 4 with 1, 2 or 3. |
| Empty title | A mission without a title cannot be shown to the rescue team. | Fill `title` with a short sentence describing the mission. |
| Empty identifier | Every mission needs an identifier to be found. | Fill `id` with a unique text, for example `radio-secours-<your-login>`. |
| Duplicate identifier | Two missions cannot share the same identifier. | `demo` is already taken: choose another one, for example `avalanche-<your-login>`. |

Outside the faulty field, **change nothing**: the proposed identifier must stay as is, unless the defect is precisely the identifier.

## Resolving the Git conflict

A conflict appears when two branches change **the same line** of the same file. Here, everyone replaces the same `TODO` block: Git cannot decide and stops.

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
>>>>>>> upstream/main
```

- `<<<<<<< HEAD` opens **your** version;
- `=======` separates the two versions;
- `>>>>>>>` closes the version coming from `main` (`upstream/main`, or `origin/main` if you used the *Sync fork* button).

**Keep both missions** (yours and the others'), delete the three marker lines and check the JSON commas and braces.

```bash
git add missions.json
git commit -m "Résout le conflit des missions"
git push
```

The check runs again automatically: it must turn green.

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

Every merged PR with a green check awards **3 points** to its author. The leaderboard is written automatically to `leaderboard.json`.

- A PR is counted **only once**.
- Existing scores are kept from one PR to the next.
- Sorted by descending points, then by login.
- **0 points** if the check is not green, or if the PR changes anything other than `missions.json`.

To view it: open `leaderboard.json`, or the **Actions** tab → **Classement** workflow (each run reports the points awarded).

## Project structure

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

No external dependencies, no secrets, no deployment steps: Python 3 and Git are all you need.

The shipped `missions.json` **fails on purpose**: it still contains the `TODO` identifier. That is the starting point of the game.
