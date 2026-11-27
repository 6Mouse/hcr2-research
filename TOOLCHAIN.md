# Android ARM64 toolchain

Use the [shared profile](toolchain.json) for every enrolled fixture. Each fixture has its own `match.json` for the symbol, byte size and reference hashes. Fixture manifests cannot override the shared profile.

Install Android NDK **30.0.14904198 (r30 beta 1)** through Android Studio SDK Manager or `sdkmanager --install "ndk;30.0.14904198"`. The verifier requires its Clang **21.0.0** at LLVM revision `9f872551d3c681d06fd303b36f16ed5c274735eb`. It uses `clang++`, `llvm-readelf`, and `llvm-objcopy` from the same NDK. The target is `aarch64-linux-android24`, with C++17, `-O2`, and the flags checked into `toolchain.json`. The API level and optimization settings are fixture choices.

Run `python tools/verify_fixture.py --fixture fixtures/<assigned-directory>`. Add `--ndk <installed-directory>` if the NDK is outside the normal SDK path. `--reference-only` checks an unsolved fixture's locked reference without a candidate. A matching submission must pass with its candidate present and with no fixture or toolchain changes. GitHub Actions is the common Linux check for every contribution.

## What the shipped library establishes

The original ARM64 split's `libcocos2dcpp.so` matches the engine fingerprint in `baseline.json`. `llvm-readelf -h -S -n -d` reports an ELF64 AArch64 Android library with GNU build ID `4827fc26f4545795631badaff072a30540761f4b`. The packaged engine has no `.comment` or `.note.android.ident` section. The build ID identifies the artifact but gives no compiler version. The Android AArch64 target and use of ELF tools are supported by the evidence. The original compiler revision, Android target API, and optimization/linker flags remain unconfirmed. The pinned NDK is a reproducible choice for the original exercises, not a claim about the game's compiler.
