# HCR2 Research

Community work queue for offline observations and verification tools. The first milestone is an independently verified Android ARM64 1.76.1 reference. Build checks can compare contributor-owned artifacts byte for byte. The stock APK stays local to each contributor.

## Start here

Requires Python 3.10 or newer. Use your local original split archive. The verifier checks the base APK, ARM64 split and packaged engine bytes separately from the outer archive hash. A different ZIP wrapper can contain identical signed splits.

```powershell
python project.py verify-release .\local-output\HCR2-1.76.1-Original-Splits.apks
python project.py compare .\local-output\reference.o .\local-output\rebuilt.o
python project.py dashboard
```

Open `dist/index.html` for the dashboard. The compare command exits 1 on any byte difference and reports both SHA-256 values, file sizes and the first differing byte offset. Save the output, toolchain version and compiler flags as review evidence. The reference base and ARM64 split passed Android signature verification and shared a certificate. The source-kit APK failed that check and is unsuitable as the original reference.

## Contribute with an agent

1. Open a claim issue for one ID in `tasks.json`. Check the existing issues for competing claims.
2. Give your agent that task ID and ask it to read `AGENTS.md`. Use a task-specific branch or worktree.
3. Submit original tooling, observations or test fixtures in a small PR with the reproduction steps. Link the claim issue.
4. A second person reproduces the result. The maintainer updates the task record to `verified` with `contributor`, `reviewer` and an HTTPS `evidence` URL. Only verified records count toward the dashboard.

The workflow follows the shared queues and independently checked progress of [Fallout 3 Decomp](https://f3decomp.com/how) and [Fallout: New Vegas Decomp](https://fnvdecomp.com/how). The dashboard counts verified research tasks. An exact artifact match is recorded as test evidence, and the dashboard makes no claim about percentage of the game reconstructed.

## Share the project

Create a GitHub repository under the account or organization that will maintain it. Push this directory only. Enable Issues, require a human review on the default branch, and use the claim and PR templates. If publishing the dashboard, serve only the generated `dist` directory. The baseline APK, local outputs, and all historical research stay outside the published files.

Unofficial project. Hill Climb Racing 2 is used to identify the subject of the research.
