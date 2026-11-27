# HCR2 Research

Community work queue for offline observations and verification tools. The first milestone is an independently verified Android ARM64 1.76.1 reference. Build checks can compare contributor-owned artifacts byte for byte. The stock APK stays local to each contributor.

[Live progress dashboard](https://6mouse.github.io/hcr2-research/) · [Work queue](tasks.json) · [Contributor and Discord setup](LAUNCH.md)

## Start here

Clone this repository and run `python project.py check` from its root with Python 3.10 or newer. It checks the comparer, archive verifier and replay fixture, then builds `dist/index.html`. This command needs no APK, NDK, or credentials. Open the dashboard or read [the work queue](tasks.json) to pick a task.

## Original 1.76.1 reference

For tasks that need the game baseline, use the [shared HCR2 1.76.1 split archive on Google Drive](https://drive.google.com/file/d/1Df8zMPtGU62bngYAISfYo0ktUJVTL32F/view?usp=sharing). Keep it outside Git. The expected SHA-256 for the full archive is `62c5269ef6a52fc372b689cbe74a017ec595d7ddf0f791a04d9550ac07b33669`.

Use `--exact-archive` before starting a task that depends on the game baseline. It checks the full archive and the base APK, ARM64 split, and engine inside it. If verification fails, report the hashes in the task issue.

```powershell
python project.py verify-release --exact-archive 'C:\path\to\downloaded.apks'
```

For artifact comparisons, run `python project.py compare <reference> <candidate>`. It exits 1 on a byte difference and reports both SHA-256 values, file sizes and the first differing byte offset. Save the output, toolchain version and compiler flags as evidence.

## Contribute with an agent

1. Pick one open ID in `tasks.json`. Check Issues for an existing claim, then open a claim issue.
2. Give your agent the ID and `AGENTS.md`. Work on a separate branch or fork.
3. Run `python project.py check`. Submit a small PR that links the claim and contains exact reproduction steps.
4. A maintainer reviews the PR and records separate reproduction evidence. Only reviewed, reproduced work counts as verified on the dashboard.

The workflow follows the shared queues and independently checked progress of [Fallout 3 Decomp](https://f3decomp.com/how) and [Fallout: New Vegas Decomp](https://fnvdecomp.com/how). The dashboard counts verified research tasks. An exact artifact match is recorded as test evidence, and the dashboard makes no claim about percentage of the game reconstructed.

## Try the ARM64 matching pilot

HCR2-005 uses a small original C++ function. Install Android NDK `30.0.14904198` with Android Studio or `sdkmanager --install "ndk;30.0.14904198"`. Then run:

```powershell
python tools/verify_fixture.py
```

Use `--ndk <directory>` if the NDK is outside the normal SDK path. The verifier checks the compiler identity, builds the reference twice, checks the pinned object and function hashes, and compares the candidate's function bytes. A deliberately different implementation must fail the byte comparison. To try your own source, pass `--candidate <file.cpp>`. The candidate must export the C symbol `hcr2_fixture` with the signature in `fixtures/arm64/reference.cpp`.

`fixtures/arm64/match.json` records the task ID, compiler and target flags, symbol, byte count and reference hashes. To add another authorized, self-contained fixture on this NDK, create a directory under `fixtures/` with `match.json`, `reference.cpp`, `candidate.cpp`, and `nonmatch.cpp`, and assign it a stable ID in the work queue. Run `python tools/verify_fixture.py --fixture <directory>`. CI checks every fixture directory with a manifest.

The compiler and flags are fixture settings only. The verifier checks an isolated relocation-free function. `-fno-ident` omits the host-specific compiler identification string from the object. The verifier still checks and prints the pinned compiler identity. A reviewer can run the command on another machine and attach the output to the PR. CI also runs the check on Linux without the game archive.

## Share the project

See [the launch checklist](LAUNCH.md) for a copy-paste agent brief, match review rules, and Discord setup. The baseline APK, local outputs, and historical research stay outside the repository.

Unofficial project. Hill Climb Racing 2 is used to identify the subject of the research.
