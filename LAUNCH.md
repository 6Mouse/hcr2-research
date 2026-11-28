# Share and review

Share the [project page](https://6mouse.github.io/hcr2-research/). It links to the public repo, available tasks, and a [brief contributors can give their agents](https://6mouse.github.io/hcr2-research/agent.txt).

For a function match, verify and enroll the reference once, then review and squash-merge passing PRs. GitHub Actions checks and records owner merges and updates Pages and Discord. GitHub may prompt you to approve checks for a first-time contributor. [Maintainer steps](MATCHING.md#enroll-and-record)

## Accept a report

1. Review the report and reproduce the observation separately. For PRs, review the changed files before approving first-time CI runs if GitHub asks.
2. Merge the note if it was submitted as a PR. When the result is verified, add the contributor login, independent reviewer login, and evidence URL to its entry in `tasks.json`, then set the state to `verified`.
3. Commit the task change to `main`. GitHub Actions validates it and publishes the dashboard. After deployment, the webhook announces newly verified observations.

Machine-code megabytes on the dashboard refer to verified core function bytes. The core ELF's executable segment size is recorded separately as a reference measurement.

## Discord

The workflow uses the `DISCORD_MATCH_WEBHOOK` repository secret. The configured channel receives updates for newly recorded matches and verified observations. A labeled delivery test can be sent from **Actions → ARM64 core research → Run workflow** on `main` with **test_discord** enabled. Rerunning a previously successful notification job may repeat its message.
