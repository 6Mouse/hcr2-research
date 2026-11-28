# Share and review

Share the [public repo](https://github.com/6Mouse/hcr2-research) and the [dashboard](https://6mouse.github.io/hcr2-research/). Give contributors this prompt.

> Read README.md and AGENTS.md. For matching, follow MATCHING.md and choose an open function. For mechanics and diagnostics, pick an open research task and report reproducible evidence. Both tracks use the pinned HCR2 1.76.1 ARM64 core library.

For a function match, follow the [maintainer steps](MATCHING.md#enroll-and-record). Verify the reference range before opening the task and compare archive bytes before recording the match.

## Accept a report

1. Review the report and reproduce the observation separately. For PRs, review the changed files before approving first-time CI runs if GitHub asks.
2. Merge the note if it was submitted as a PR. When the result is verified, add the contributor login, independent reviewer login, and evidence URL to its entry in `tasks.json`, then set the state to `verified`.
3. Commit the task change to `main`. GitHub Actions validates it and publishes the dashboard. After deployment, the webhook announces newly verified observations.

Machine-code megabytes on the dashboard refer to verified core function bytes. The core ELF's executable segment size is recorded separately as a reference measurement.

## Discord

The workflow uses the `DISCORD_MATCH_WEBHOOK` repository secret. The configured channel receives updates for newly recorded matches and verified observations. A labeled delivery test can be sent from **Actions → ARM64 core research → Run workflow** on `main` with **test_discord** enabled. Rerunning a previously successful notification job may repeat its message.
