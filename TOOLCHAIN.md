# Android ARM64 toolchain

Use the [shared profile](toolchain.json) for every enrolled fixture. Each fixture has its own `match.json` for the symbol, byte size and reference hashes. Fixture manifests cannot override the shared profile.

Install Android NDK **27.3.13750724 (r27d)** through Android Studio SDK Manager or `sdkmanager --install "ndk;27.3.13750724"`. The verifier requires Android Clang **18.0.4** (`r522817d`, LLVM revision `d8003a456d14a3deb8054cdaa529ffbf02d9b262`). It uses `clang++`, `llvm-readelf`, and `llvm-objcopy` from the same NDK. The target is `aarch64-linux-android24`, with C++17, `-O2`, and the flags checked into `toolchain.json`. The API level and optimization settings are fixture choices. [Android NDK r27d release](https://github.com/android/ndk/releases/tag/r27d)

Run `python tools/verify_fixture.py --fixture fixtures/<assigned-directory>`. Add `--ndk <installed-directory>` if the NDK is outside the normal SDK path. `--reference-only` checks an unsolved fixture's locked reference without a candidate. A matching submission must pass with its candidate present and with no fixture or toolchain changes. GitHub Actions is the common Linux check for every contribution.

## What the shipped library establishes

The original ARM64 split's `libcocos2dcpp.so` matches the engine fingerprint in `baseline.json`. `llvm-readelf -h -S -n -d` reports ELF64, AArch64, Android system libraries and GNU build ID `4827fc26f4545795631badaff072a30540761f4b`. The engine has no `.comment` or `.note.android.ident` section. A scan of the packaged engine bytes found compiler strings for Android Clang 18.0.4 (`r522817d`, build `13691557`), Android Clang 17.0.2 (`r487747e`), and an LLVM 5.0-based Clang. Google identifies `r522817d` as the compiler in NDK r27d. That makes r27d a close evidenced choice for the fixture workflow. The strings do not establish which compiler built particular functions or which Android API level, optimization flags, linker settings, or linker inputs the developers used. [Android NDK r27 changelog](https://github.com/android/ndk/wiki/Changelog-r27)
