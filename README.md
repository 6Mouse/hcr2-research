# HCR2 Research

Community work queue for offline observations and verification tools. The first milestone is an independently verified Android ARM64 1.76.1 reference. Build checks can compare contributor-owned artifacts byte for byte. The stock APK stays local to each contributor.

[Live progress dashboard](https://6mouse.github.io/hcr2-research/) · [Shipped library inventory](release_inventory.json) · [Shared toolchain](TOOLCHAIN.md) · [Contributor and Discord setup](LAUNCH.md)

## Start here

Clone this repository and run `python project.py check` from its root with Python 3.10 or newer. It checks the comparer, archive verifier and replay fixture, then builds `dist/index.html`. This command needs no APK, NDK, or credentials. Open the dashboard or read [the work queue](tasks.json) to pick a task.

## Original 1.76.1 reference

For tasks that need the game baseline, use the [shared HCR2 1.76.1 split archive on Google Drive](https://drive.google.com/file/d/1Df8zMPtGU62bngYAISfYo0ktUJVTL32F/view?usp=sharing). Keep it outside Git. The expected SHA-256 for the full archive is `62c5269ef6a52fc372b689cbe74a017ec595d7ddf0f791a04d9550ac07b33669`.

Use `--exact-archive` before starting a task that depends on the game baseline. It checks the full archive and the base APK, ARM64 split, and engine inside it. If verification fails, report the hashes in the task issue.

```powershell
python project.py verify-release --exact-archive 'C:\path\to\downloaded.apks'
```

The [shipped library inventory](release_inventory.json) covers every native library entry across the archive's ARM64, ARMv7 and x86-64 splits. It records APK entry paths, SHA-256 hashes, exact file sizes, file-backed executable segment sizes, and the ELF symbol and unwind counts the pinned `llvm-readelf` can read. A JSON `null` means a value was unavailable or unmeasured. Unwind index entries can cover partial functions or other code ranges, and executable segments can also contain non-code bytes. The complete shipped function count and total function bytes are therefore unmeasured.

Regenerate the inventory from the local archive after installing the [pinned NDK](TOOLCHAIN.md). The command verifies the archive and reads the packaged ELF headers, symbols and unwind metadata without launching the game.

```powershell
python -m tools.release_inventory 'C:\path\to\downloaded.apks' --output release_inventory.json
```

For artifact comparisons, run `python project.py compare <reference> <candidate>`. It exits 1 on a byte difference and reports both SHA-256 values, file sizes and the first differing byte offset. Save the output, toolchain version and compiler flags as evidence.

The [historical reference](HISTORICAL_REFERENCE.md) reproduces a four-byte upstream Cocos2d-x accessor inside the original 1.7.0 ARMv7 library. Its scope and progress totals are separate from 1.76.1. Follow the [agent guidance](AGENTS.md) when giving functions or variables provisional names.

## Contribute with an agent

1. Choose any open test fixture in the [fixture catalog](function_catalog.json). You can start immediately, even if someone else is working on the same function. For other research, choose an open ID in `tasks.json` and use the research claim form.
2. Give your agent the ID, `AGENTS.md` and the fixture's `TASK.md`. Work on a separate branch or fork.
3. Put the solution in the fixture's `candidate.cpp`. From the repo root run `python -m tools.verify_fixture --function HCR2-NNN` with your ID, then run `python project.py check`.
4. Open a PR titled `[HCR2-NNN] Match <symbol>` with the `match.json` path, the exact command and its `MATCH` line. That line includes the stable ID, ELF symbol and section, byte count, and code SHA-256. CI repeats the byte check with the pinned compiler.
5. The repository owner reviews and merges the PR. GitHub Actions rechecks the exact match on `main`, records it, and updates the verified pool and dashboard.

The workflow follows the shared queues and independently checked progress of [Fallout 3 Decomp](https://f3decomp.com/how) and [Fallout: New Vegas Decomp](https://fnvdecomp.com/how). The dashboard counts verified research tasks. An exact artifact match is recorded as test evidence, and the dashboard makes no claim about percentage of the game reconstructed.

## Try the ARM64 matching pilot

HCR2-005 uses a small original C++ function. Install Android NDK `27.3.13750724` with Android Studio or `sdkmanager --install "ndk;27.3.13750724"`. Then run:

```powershell
python -m tools.verify_fixture --function HCR2-005
```

Use `--ndk <directory>` if the NDK is outside the normal SDK path. The verifier checks the compiler identity, builds the reference twice, checks the pinned object and function hashes, and compares the candidate's function bytes. A deliberately different implementation must fail the byte comparison. To try your own source, pass `--candidate <file.cpp>`. The candidate must export the C symbol `hcr2_fixture` with the signature in `fixtures/arm64/reference.cpp`.

`toolchain.json` records the compiler and target flags for all fixtures. Each `match.json` records the task ID, symbol, byte count, and reference hashes. To enroll another original or authorized, self-contained fixture, propose a directory under `fixtures/` with `match.json`, `reference.cpp`, `nonmatch.cpp`, and `TASK.md`. The owner adds the stable ID to the function catalog. CI checks the locked reference first and checks `candidate.cpp` once submitted.

The compiler and flags are fixture settings only. The verifier checks an isolated relocation-free function. `-fno-ident` omits the host-specific compiler identification string from the object. The verifier still checks and prints the pinned compiler identity. A reviewer can run the command on another machine and attach the output to the PR. CI also runs the check on Linux without the game archive.

## Share the project

See [the launch checklist](LAUNCH.md) for a copy-paste agent brief, match review rules, and Discord setup. The baseline APK, local outputs, and historical research stay outside the repository.

Unofficial project. Hill Climb Racing 2 is used to identify the subject of the research.
