# HCR2-006 · Rotate-byte fixture

This is an original 32-bit unsigned expression compiled to Android ARM64. Express the same bit operations independently in `candidate.cpp` as `extern "C" unsigned rotate_byte(unsigned value)`. The output keeps the low eight bits after OR-ing the input shifted left by three with the input shifted right by five. The input is a full unsigned integer.

Check with `python -m tools.verify_fixture --function HCR2-006`. Submit only the candidate and put the verification evidence in the PR description. The reference, negative control and their hashes are shared inputs.
