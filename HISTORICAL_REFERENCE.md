# One stock 1.7.0 byte match

The original 1.7.0 ARMv7 APK exports `cocos2d::Rect::getMinX() const` (`_ZNK7cocos2d4Rect7getMinXEv`) from `lib/armeabi-v7a/libcocos2dcpp.so`. The symbol covers **4 bytes** in `.text`. The public upstream accessor returns the X coordinate of the rectangle's origin. [Cocos2d-x reference](https://raw.githubusercontent.com/cocos2d/cocos2d-x/v3/cocos/math/CCGeometry.cpp)

The [C++ wrapper](fixtures/historical/rect_min_x.cpp) compiled to the exact four bytes in the local stock APK. A second wrapper that reads Y differed, despite compiling to the same length. An exact match establishes byte equality for this routine on this ABI. The engine version, compiler used by the original developer for this function, and corresponding routine in 1.76.1 are unknown.

## Reproduce locally

Keep your stock copy outside Git and install the [pinned NDK](TOOLCHAIN.md). From the repository root run the verifier against your local APK.

```powershell
python -m tools.verify_historical_example 'C:\path\to\original-1.7.0.apk'
```

The script verifies the APK, locates the symbol by name, verifies the reference function hash, and compares the compiled C++ candidate byte for byte. It uses Clang 18.0.4 with `--target=armv7a-linux-androideabi21 -mthumb -O2 -ffunction-sections` for this historical check.

| Artifact | SHA-256 |
| --- | --- |
| Original 1.7.0 APK | `4c4f911b1e166230fc2c50c133b0783fef96c541410e16971938c0d878a774ed` |
| ARMv7 library | `4c28e263a414e709bbb6850039a87050aa25e135eada3cdc371c86020b14df52` |
| Function bytes | `a89b85f8bccd76763270edbe8d4a9000e557118189ef0a663b750b93593d16da` |

## Progress totals

| Scope | Verified functions | Verified code bytes |
| --- | ---: | ---: |
| 1.7.0 ARMv7 historical example | 1 of 1 | 4 of 4 |
| 1.76.1 ARM64 shipped game | 0 verified, total unknown | 0 verified, total unknown |

The 1.76.1 packaged ARM64 engine has **36,384,356 file-backed executable segment bytes** and **105,543 unwind index entries**. Executable segments include non-function data, and unwind entries can cover partial functions. These measurements describe the library and do not establish the exact denominators for matching. [1.76.1 inventory](release_inventory.json)
