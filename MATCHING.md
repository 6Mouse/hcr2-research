# Match a core function

This track covers selected, self-contained math and utility routines from the pinned HCR2 **1.76.1 arm64-v8a** core. The source tree holds one C++ candidate per enrolled function. Reference bytes stay in your local copy of the original archive.

## Contribute

1. Pick an open function from the [dashboard](https://6mouse.github.io/hcr2-research/#matching) or run `python -m tools.match_core list`. The first entry needs a reviewed reference range before it appears.
2. Install Android NDK **27.3.13750724 (r27d)**. Write the candidate at the path listed for the function. Use the catalog symbol with `extern "C"` so the checker finds it. Use readable C++ and explain uncertain names or behavior with an `Inferred` comment. Keep the routine self-contained. Inline assembly, embedded byte sequences, and compiler tricks used solely to force a match are outside the review standard.
3. Run `python -m tools.match_core check ARM64-001` with your ID. Add `--archive "C:\path\to\HCR2-1.76.1.apks"` for a direct byte comparison. If the NDK is outside the default SDK location, add `--ndk` with its path.
4. Submit just the candidate source in a PR named `[ARM64-001] Match <symbol>`. Paste the check result in the description. CI recompiles and checks the code section's length and SHA-256 against the reviewed catalog entry.

## Enroll and record

The maintainer reviews the role and exact file boundaries for a selected routine. `--offset` is a **file offset in `libcocos2dcpp.so`**. For the example command, replace the offset, byte count, note, and archive path with verified information. Leave a candidate out of the catalog when its boundaries or provenance are uncertain.

```powershell
python -m tools.match_core enroll ARM64-001 example_name --offset 0x1000 --size 16 --note "Explain the verified function boundary and role" --archive "C:\path\to\HCR2-1.76.1.apks"
```

Review and commit `core_matches.json` to open that task. The command pins the raw archive range to its hash. The [toolchain file](toolchain.json) defines the compiler used for this pilot. The original 1.76.1 build flags remain unverified.

Review and merge a passing candidate PR. Run the following command with that PR's ID and URL to check the exact reference bytes and record the match.

```powershell
python -m tools.match_core record ARM64-001 --archive "C:\path\to\HCR2-1.76.1.apks" --evidence "https://github.com/6Mouse/hcr2-research/pull/123"
```

Commit `core_matches.json` to `main` again. Pages publishes the enrolled and verified bytes in decimal MB, and the configured Discord webhook gets an update. Overlapping reference ranges are rejected. The whole-core machine-code total remains unmeasured.
