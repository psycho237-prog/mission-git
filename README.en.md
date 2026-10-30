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

> Golden rule: only edit `missions.json`. Never touch `check_missions.py`, `cartes.json`, `update_leaderboard.py` or the workflows — that would bypass the validation.

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

## Facilitation rule (essential)

> **All branches must be created from the same state of `main`, and all PRs must be opened before the first PR is merged.**

This simultaneity is what creates the teaching conflict. If PRs are opened and merged one by one, no conflict appears and the exercise loses its point. Watch the PRs and only merge one once everyone has theirs.

Fallback if the conflict does not appear: ask **two participants to edit exactly the same `TODO` block** (this already happens by design: every card replaces that block).

## Automatic leaderboard

Every merged PR that passed the **Mission check** check awards **3 points** to its GitHub author. The leaderboard is written automatically to `leaderboard.json` by the **Classement** workflow.

### Scoring rules

- **3 points** per merged PR whose validation check is green at merge time.
- Existing scores are **preserved**: the file is extended, never reset.
- A PR is counted **only once**: its number is stored in `prs`, so re-running the workflow adds nothing.
- The leaderboard is **sorted by descending points**; ties are ordered alphabetically by login.
- A merged PR with no green check — or no check at all, for example from an unapproved fork — scores **0 points**: the workflow stops with an explicit message and changes nothing.

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

### Two separate workflows, for safety

| Workflow | Trigger | Permissions | Code executed |
| --- | --- | --- | --- |
| **Mission check** (validation) | PR `opened`, `synchronize`, `reopened` | `contents: read` | the PR code (`check_missions.py`) |
| **Classement** | `pull_request_target`, PR closed **and merged** | `contents: write` | the base branch only (`update_leaderboard.py`) |

The validation workflow runs the PR code, so it has **read access only**. The leaderboard workflow holds write access, but it **never** fetches the PR code: `actions/checkout` explicitly targets the base branch, the author and PR number come from the event payload, and the script executed is the one from the base branch. No PR code runs with a write token.

> **Branch protection caveat:** the leaderboard workflow pushes a commit to `main`. If you enable a rule that forbids direct pushes, allow the `github-actions[bot]` bot (or the workflow) to push, otherwise the leaderboard stays stuck.

## PRs from forks: what to know

The game works with forks, but GitHub can complicate validation:

- depending on the repository settings, a workflow on a PR from a fork may require **manual approval** before starting;
- without a workflow run there is no card displayed and no green check, hence **0 points** on the leaderboard;
- the validation workflow uses the workflow file from the PR (`pull_request` event), so the base repository must already contain the workflow before people fork.

Simplest and safest workshop option: participants can always run `python3 check_missions.py --auteur <login>` locally to learn their card and check their file, and the facilitator approves runs in the **Actions** tab. Also check the fork workflow approval setting under *Settings → Actions → General*.

## Checking the project locally

```bash
python3 check_missions.py --auteur <your-login>
```

The shipped `missions.json` **fails on purpose**: it still contains the `TODO` identifier. That is the starting point of the game.

## Project structure

```
mission-git/
├── README.md
├── README.en.md
├── missions.json
├── cartes.json
├── check_missions.py
├── leaderboard.json
├── update_leaderboard.py
└── .github/
    └── workflows/
        ├── mission-check.yml
        └── leaderboard.yml
```

No external dependencies, no secrets, no deployment steps: Python 3 and Git are all you need.

---

# Facilitator-only section

> Do not share the solutions below with participants before the end of the exercise.

## Card solutions

Each card contains **exactly one** defect. Fixing it means touching only the faulty field.

| Card | Expected mission | Voluntary defect | Fix |
| --- | --- | --- | --- |
| `colis-perdu` <br>(e.g. `david`) | Retrouver un colis égaré en zone urbaine | `difficulty` is `4` | Set `1`, `2` or `3` (the card's value: `2`) |
| `pont-effondre` <br>(e.g. `rose`) | Rétablir un pont piéton effondré | `title` is empty | Write "Rétablir un pont piéton effondré" (or any non-empty title) |
| `radio-secours` <br>(e.g. `alice`) | Rétablir la radio de secours | `id` is empty | Set `radio-secours-<login>` |
| `avalanche` <br>(e.g. `bob`) | Dégager une route bloquée par une avalanche | `id` is `demo` (duplicate) | Set `avalanche-<login>` |

Example of a fully corrected file (login `david`, card `colis-perdu`):

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

## Check the assignment before the workshop

To know each participant's card:

```bash
python3 check_missions.py --auteur <login> | head -4
```

The assignment is `sum of the login letter codes, modulo 4`. Over many logins the four cards are used almost equally; two participants can share a card without trouble, since their identifiers differ.

## Game integrity

- Explicitly ask participants **not to modify** `check_missions.py`, `cartes.json`, `update_leaderboard.py` or `.github/workflows/`.
- The `Vérifier les missions` check runs the PR's own code, so a PR that edits `check_missions.py` can turn it green. Review the changed files before merging. The leaderboard workflow refuses points anyway to any PR that changes anything other than `missions.json`.
- The validation workflow runs with `contents: read` only: it cannot write anything to the repository.
