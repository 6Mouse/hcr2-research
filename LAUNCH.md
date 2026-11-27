# Launch checklist

The starter can be prepared by one maintainer. It includes the source, the validation commands, the work queue, and both tested pilots. The first outside contribution can wait until after launch.

## Share the project

Share the [repository](https://github.com/6Mouse/hcr2-research) and [live progress dashboard](https://6mouse.github.io/hcr2-research/). GitHub Actions checks the starter and builds the dashboard on `main`. `python project.py check` also runs locally without game files or an NDK. Choose a license for the original tooling and documentation before collecting code for an open-source release.

## Invite the first contributor

Send the repo link with this brief:

> Clone the repo, run `python project.py check`, and pick one open task in `tasks.json`. Read `AGENTS.md`, claim the task in Issues, and work on a separate branch. For an enrolled ARM64 fixture, inspect its `match.json` and validate your candidate with `python tools/verify_fixture.py --fixture fixtures/<name> --candidate <candidate.cpp>`. Open a PR with the task ID, the exact command and its result. Use original code or reference material we have permission to rebuild and publish. Keep game assets and private inputs out of the PR.

Keep acceptance decisions in PRs. Enroll each function once in `function_catalog.json`, with its stable task ID, symbol, and exact reference size. Establish the target set up front so the percentages have a clear denominator. When a match passes the pinned checker and a maintainer accepts it, add its fixture directory, `matched_on` date, and verification URL to that entry. CI checks the manifest and candidate before deployment.

The dashboard calculates `matched_functions / total_functions` and `matched_bytes / total_bytes` separately. It displays decimal MB (1 MB = 1,000,000 bytes) and exact byte counts. Scope is original ARM64 fixtures. The shipped game's progress remains unmeasured.

## Enable Discord updates

1. In Discord, open the destination channel's settings, then **Integrations → Webhooks → New Webhook**. Copy its URL.
2. Open [GitHub Actions secrets](https://github.com/6Mouse/hcr2-research/settings/secrets/actions). Add a repository secret called `DISCORD_MATCH_WEBHOOK` and paste the URL there.
3. In [Actions → ARM64 matching pilot](https://github.com/6Mouse/hcr2-research/actions/workflows/arm64-fixture.yml), choose **Run workflow** on `main` and enable **test_discord**. Confirm the labeled test appears in Discord.

After a successful push to `main`, the workflow announces newly matched IDs with the symbol, exact byte count, match date, and both cumulative progress totals. Existing matches are not sent when you add the secret. Re-running a successful notification job for the same push may send those messages again.

## What the results cover

- HCR2-003 passed independent reproduction on synthetic coordinates, including the one injected jump at 16 km. It does not test real game replays.
- HCR2-005 built identical reference objects on Windows and a separate Linux runner. The function bytes matched and a changed candidate failed. The task remains in review, with the CI run linked as evidence.
- The original 1.76.1 split archive has pinned hashes in `baseline.json`. The matching compiler and flags apply to the original pilot fixture. The project has not established the shipped game's compiler settings, an exact match to a shipped function, or a game rebuild pipeline.
