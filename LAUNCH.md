# Share and review

Share the [public repo](https://github.com/6Mouse/hcr2-research) and the [dashboard](https://6mouse.github.io/hcr2-research/). Give contributors this prompt.

> Read README.md and AGENTS.md. Pick any open task about the pinned HCR2 1.76.1 ARM64 core library. Verify your local copy first, then submit the command, engine fingerprint, measurements, and any uncertainties as a GitHub issue or a short Markdown note. Start with HCR2-001 if you're new.

## Accept a report

1. Review the report and reproduce the observation separately. For PRs, review the changed files before approving first-time CI runs if GitHub asks.
2. Merge the note if it was submitted as a PR. When the result is verified, add the contributor login, independent reviewer login, and evidence URL to its entry in `tasks.json`, then set the state to `verified`.
3. Commit the task change to `main`. GitHub Actions validates it and publishes the dashboard. After deployment, the webhook announces newly verified observations.

Machine-code megabytes on the dashboard refer to verified core function bytes. The core ELF's executable segment size is recorded separately as a reference measurement.

## Discord

The workflow uses the `DISCORD_MATCH_WEBHOOK` repository secret. The configured channel receives updates when a core observation is newly marked verified. A labeled delivery test can be sent from **Actions → ARM64 core research → Run workflow** on `main` with **test_discord** enabled. Rerunning a previously successful notification job may repeat its message.
