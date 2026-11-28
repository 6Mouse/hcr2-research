# Launch checklist

The starter can be prepared by one maintainer. It includes the source, the validation commands, the work queue, and both tested pilots. The first outside contribution can wait until after launch.

## Share the project

Share the [public repository](https://github.com/6Mouse/hcr2-research) and [live progress dashboard](https://6mouse.github.io/hcr2-research/). GitHub Actions checks the starter and builds the dashboard on `main`. `python project.py check` also runs locally without game files or an NDK. The repository does not include a project license.

## Invite the first contributor

Send the repo link with this brief:

> Clone the repo and read `AGENTS.md` and `TOOLCHAIN.md`. Pick any open function in `function_catalog.json` and read its fixture's `TASK.md`. Write `candidate.cpp`, verify it with `python -m tools.verify_fixture --function HCR2-NNN`, and open a PR titled `[HCR2-NNN] Match <symbol>`. Include the path to `match.json`, your command and the `MATCH` line. Use only enrolled original or authorized references. Keep game binaries, assets and private inputs out of the PR.

Agents can work on the same function in parallel. Submit one function per PR so its evidence and review are easy to find. The catalog and fixture manifests give everyone the same identifiers and reference fingerprints.

### Record an accepted match

Review the tagged PR and merge its candidate after the ARM64 check passes. As the repository owner, check out and update `main`, then run the commands below with the submitted ID and the URL to the reviewed PR or verification run.

```powershell
git switch main
git pull --ff-only
python -m tools.record_match HCR2-006 --evidence 'https://github.com/6Mouse/hcr2-research/pull/123'
git diff -- function_catalog.json
git add function_catalog.json
git commit -m "Record verified match HCR2-006"
git push origin main
```

The command recompiles the checked-in candidate and records the date and evidence after an exact match. It writes the local catalog only. Add `--ndk <directory>` if needed. GitHub Actions rebuilds the fixtures before publishing the updated progress. Contributor PRs that edit the progress catalog fail the submission check.

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
