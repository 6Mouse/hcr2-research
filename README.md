# HCR2 Research

Community work queue for offline observations and verification tools. The first milestone is an independently verified Android ARM64 1.76.1 reference. Build checks can compare contributor-owned artifacts byte for byte. The stock APK stays local to each contributor.

## Start here

Requires Python 3.10 or newer. Use the [shared HCR2 1.76.1 split archive on Google Drive](https://drive.google.com/file/d/1Df8zMPtGU62bngYAISfYo0ktUJVTL32F/view?usp=sharing). Keep it outside Git. The expected SHA-256 for the full archive is `62c5269ef6a52fc372b689cbe74a017ec595d7ddf0f791a04d9550ac07b33669`.

Use `--exact-archive` before starting a task. It checks the full archive and the base APK, ARM64 split, and engine inside it. Google Drive currently returns a download quota error, so the Drive copy still needs its hash checked against the verified local reference. If the download or verification fails, report that in the task issue.

```powershell
python project.py verify-release --exact-archive '.\local-output\Hill Climb Racing 2 1.76.1 @Lan9118.apks'
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

## Try the ARM64 matching pilot

HCR2-005 uses a small original C++ function. Install Android NDK `30.0.14904198` with Android Studio or `sdkmanager --install "ndk;30.0.14904198"`. Then run:

```powershell
python tools/verify_fixture.py
```

Use `--ndk <directory>` if the NDK is outside the normal SDK path. The verifier checks the compiler identity, builds the reference twice, checks the pinned object and function hashes, and compares the candidate's function bytes. A deliberately different implementation must fail the byte comparison. To try your own source, pass `--candidate <file.cpp>`. The candidate must export the C symbol `hcr2_fixture` with the signature in `fixtures/arm64/reference.cpp`.

`fixtures/arm64/match.json` records the task ID, compiler and target flags, symbol, byte count and reference hashes. To add another authorized, self-contained fixture on this NDK, create a directory under `fixtures/` with `match.json`, `reference.cpp`, `candidate.cpp`, and `nonmatch.cpp`, and assign it a stable ID in the work queue. Run `python tools/verify_fixture.py --fixture <directory>`. CI checks every fixture directory with a manifest.

The compiler and flags are fixture settings only. The verifier checks an isolated relocation-free function. A reviewer can run the command on another machine and attach the output to the PR. CI also runs the check on Linux without the game archive.

## Share the project

Create a GitHub repository under the account or organization that will maintain it. Push this directory only. Enable Issues, require a human review on the default branch, and use the claim and PR templates. If publishing the dashboard, serve only the generated `dist` directory. The baseline APK, local outputs, and all historical research stay outside the published files.

Unofficial project. Hill Climb Racing 2 is used to identify the subject of the research.
