# HCR2 1.76.1 ARM64 Core Research

An unofficial project for reproducible offline mechanics tests and diagnostics for `lib/arm64-v8a/libcocos2dcpp.so` from Hill Climb Racing 2 **1.76.1**. Choose a task about this build and library. Use a local, unmodified copy of the game for experiments.

[Live dashboard](https://6mouse.github.io/hcr2-research/) · [Open tasks](tasks.json) · [Core ELF report](release_inventory.json) · [Maintainer guide](LAUNCH.md)

## Start here

1. Clone or download this repository. Open a terminal in the repository folder. Install Python 3.10 or newer if needed.
2. Verify your local 1.76.1 APKS archive. Replace the example path with your file.

   ```powershell
   python project.py verify-release --exact-archive "C:\path\to\HCR2-1.76.1.apks"
   ```

3. Pick any open task from the [dashboard](https://6mouse.github.io/hcr2-research/#tasks). For a first task, pick **HCR2-001** and reproduce the core SHA-256. No claim or assignment is needed.
4. Report the task ID, what you ran, and what you observed. Open a GitHub issue using **Core observation** or submit a Markdown note under `notes/`, for example `notes/HCR2-001-check.md`. Keep the APK, shipped library, account data, and raw binaries on your machine.

For the ELF report task, install Android NDK **27.3.13750724 (r27d)** using Android Studio's SDK Manager. Then run the command below. If the NDK is in a custom location, add `--ndk "C:\path\to\ndk\27.3.13750724"`.

```powershell
python -m tools.release_inventory "C:\path\to\HCR2-1.76.1.apks" --output local-output/core.json
```

Compare that JSON with the [published report](release_inventory.json). For repository checks and a local dashboard, run `python project.py check` and open `dist/index.html`. These checks need Python only.

## Test a mechanic

Record the build, track, vehicle, loadout, setup, and units. Run a baseline offline, change one input, and repeat both cases. Add the raw measurements and their precision to your note. Say whether the result is an observation, a proposed rule, or an unresolved question. When you infer a formula, list the inputs tested and the cases where the prediction disagreed.

## Read the numbers

The dashboard reports verified machine code in decimal MB (1 MB = 1,000,000 bytes). The core file's executable segments include data and padding. The complete function machine-code total is unmeasured. Verified mechanics notes have their own count.
