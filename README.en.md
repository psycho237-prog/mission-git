# Mission Git

[Français](README.md) · **English**

A 30-minute workshop game for learning pull requests, GitHub Actions checks and Git conflict resolution.

## The scenario

A rescue team must leave on a mission, but its mission board is incomplete. Your team has to **add a mission** to `missions.json` before departure is allowed.

Each participant works on their own branch and opens their own pull request (PR). A robot (GitHub Actions) checks the file automatically on every PR. When several people edit the same part of the file, Git raises a **conflict** — that is the heart of the game.

## Validation rules

The `check_missions.py` script verifies that:

- `missions.json` exists and contains valid JSON;
- the `missions` key is a list of **at least two missions**;
- each mission has a non-empty `id`, a non-empty `title`, and an integer `difficulty` equal to **1, 2 or 3**;
- the `TODO` identifier is forbidden (replace it with the name of your mission);
- identifiers are **unique**.

On any mismatch, the script prints the errors in French and exits with a non-zero status code. The GitHub Actions check then turns red.

### Winning condition

Your PR wins when:

1. the **Mission check** check is green;
2. your mission is actually present in `missions.json`;
3. your branch is up to date with `main` (conflict resolved and fix pushed).

The workshop is successful when every team PR is green and merged.

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

The validation workflow runs the PR code, so it has **read access only**. The leaderboard workflow holds write access, but it **never** fetches the PR code: `actions/checkout` explicitly targets the base branch, the author and PR number come from the event payload, and the leaderboard script (`update_leaderboard.py`) is the one from the base branch. A PR therefore cannot alter the code that runs with the write token.

> **Branch protection caveat:** the leaderboard workflow pushes a commit to `main`. If you enable a rule that forbids direct pushes, allow the `github-actions[bot]` bot (or the workflow) to push, otherwise the leaderboard stays stuck.

## Example of a valid mission

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

In this example the `TODO` has been replaced by a real mission: the `sauvetage-montagne` identifier is unique, the title is explicit and the difficulty is 3.

## Setting up the workshop (facilitator)

1. Create the repository on GitHub from this folder.
2. Check that the **Actions** tab is enabled.
3. Make sure everyone starts from the same state of `main`.

## A participant's journey

### 1. Create your branch from the same state of `main`

```bash
git clone <repository-url>
cd mission-git
git switch -c mission/<your-first-name>
```

### 2. Edit `missions.json`

Replace the `TODO` block with your own mission (unique identifier, clear title, difficulty from 1 to 3).

### 3. Check locally before pushing

```bash
python3 check_missions.py
```

The message `Bravo ! Les 2 missions sont valides.` (or more) means everything is fine.

### 4. Commit and push

```bash
git add missions.json
git commit -m "Ajoute la mission <nom>"
git push -u origin mission/<your-first-name>
```

### 5. Open the pull request

- On GitHub, click **Compare & pull request**.
- Suggested title: `Mission : <mission name>`.
- Open the PR **against `main`**.

### 6. Read the workflow result

- The PR **Checks** tab, or the repository **Actions** tab.
- Green = all good. Red = click the **Vérifier les missions** job to read the error printed by the script.

## Resolving the conflict (the highlight of the game)

Once the first participant has merged their PR, bring your branch up to date:

```bash
git fetch origin
git merge origin/main
```

Git then reports a conflict on `missions.json`:

```
CONFLICT (content): Merge conflict in missions.json
Automatic merge failed; fix conflicts and then commit the result.
```

### Understanding conflict markers

Open `missions.json`: Git has inserted markers in the affected block.

```
<<<<<<< HEAD
      "id": "votre-mission",
      "title": "Votre titre",
=======
      "id": "mission-du-voisin",
      "title": "Le titre du voisin",
>>>>>>> origin/main
```

- `<<<<<<< HEAD` opens **your** version (the current branch);
- `=======` separates the two versions;
- `>>>>>>> origin/main` closes the version coming from `main`.

You must **choose, combine or rewrite** the block, then **delete the three marker lines**. The final file must remain valid JSON, with both missions kept and unique identifiers.

### Save the fix

After resolving:

```bash
git add missions.json
git commit -m "Résout le conflit des missions"
git push
```

The check automatically runs again on the PR (`synchronize`): it must turn green again.

## Workshop schedule (30 minutes)

| Time | Step |
| --- | --- |
| 0-3 min | Welcome, rescue team scenario, repository walkthrough. |
| 3-8 min | Demo: branch, edit, PR, green check. |
| 8-15 min | Participants create their branch, edit `missions.json` and open their PR. |
| 15-18 min | The facilitator merges the first PR: the conflict appears for everyone else. |
| 18-26 min | Everyone updates `main`, resolves the conflict, pushes the fix and sees their check turn green again. |
| 26-30 min | Merge the remaining PRs, wrap up: PRs, checks, conflicts, good practices. |

## Facilitation rule (essential)

> **All participants must create their branch from the same state of `main` and open their PR before the first PR is merged.**

This simultaneity is what creates the teaching conflict. If PRs are opened and merged one by one, no conflict appears and the exercise loses its point. So watch for PRs to be opened and only merge the first one once everyone has theirs.

## Fallback option if the conflict does not appear

Ask **two participants to edit exactly the same `TODO` block**, at the same place in the file, with different identifiers. The conflict is then guaranteed, even if the rest of the file differs.

Other troubleshooting: check that participants really ran `git fetch origin` then `git merge origin/main` (and not `git pull` on a branch that was never linked).

## Practical warning: PRs coming from forks

GitHub Actions checks on a PR opened from a **fork** may depend on the repository settings:

- for external contributors, GitHub may require **manual approval** before running the workflow;
- secrets are not passed to workflows triggered by a fork;
- depending on the repository configuration, the workflow may not run at all.

For a workshop without surprises, the simplest option is for participants to be **repository collaborators** and push their branches directly to the repository (not from a fork). Otherwise, plan to approve runs manually in the **Actions** tab.

## Checking the project locally

```bash
python3 check_missions.py
```

The shipped `missions.json` **fails on purpose**: it still contains the `TODO` identifier. That is the starting point of the game. The script prints an error and exits with a non-zero status code.

## Project structure

```
mission-git/
├── README.md
├── README.en.md
├── missions.json
├── check_missions.py
├── leaderboard.json
├── update_leaderboard.py
└── .github/
    └── workflows/
        ├── mission-check.yml
        └── leaderboard.yml
```

No external dependencies, no secrets, no deployment steps: Python 3 and Git are all you need.
