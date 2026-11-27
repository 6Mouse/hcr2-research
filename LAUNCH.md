# Launch checklist

The starter can be prepared by one maintainer. It includes the source, the validation commands, the work queue, and both tested pilots. The first outside contribution can wait until after launch.

## Before sharing

1. Run `python project.py check` from a fresh checkout or extracted ZIP. Open the generated `dist/index.html` if you want the dashboard.
2. Decide whether to license the original tooling and documentation for reuse. The game archive has its own provenance and stays outside the repository. Agree on contributor licensing before collecting code for an open-source release.
3. When ready, publish the prepared commits or share the source ZIP. For the existing GitHub repo, an ordinary fast-forward push from `release-starter` to `main` publishes the prepared branch. If `main` has moved, inspect and integrate those changes first. Keep the existing history.

## Invite the first contributor

Send the repo link with this brief:

> Clone the repo, run `python project.py check`, then pick one open task in `tasks.json`. Read `AGENTS.md`, claim the task in Issues, and open a PR with exact reproduction steps. The starter check requires only Python.

Keep acceptance decisions in PRs. GitHub Actions runs the ARM64 build check and the starter tests. For a future group launch, require reviewed PRs and passing checks on `main`. Hosting the dashboard is optional.

## What the results cover

- HCR2-003 passed independent reproduction on synthetic coordinates, including the one injected jump at 16 km. It does not test real game replays.
- HCR2-005 built identical reference objects on Windows and a separate Linux runner. The function bytes matched and a changed candidate failed. The task remains in review, with the CI run linked as evidence.
- The original 1.76.1 split archive has pinned hashes in `baseline.json`. The matching compiler and flags apply to the original pilot fixture. The project has not established the shipped game's compiler settings, an exact match to a shipped function, or a game rebuild pipeline.
