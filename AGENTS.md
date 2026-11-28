# Contributor agents

For matching, follow [MATCHING.md](MATCHING.md). Pick an open function in `core_matches.json`, run the pinned verifier, and submit only its candidate source. Byte equality and the evidence for inferred names are separate review items.

For observational research, read [README.md](README.md) and [tasks.json](tasks.json). The target is the pinned **1.76.1 arm64-v8a** core library `lib/arm64-v8a/libcocos2dcpp.so`. Pick an open task without claiming it. Submit your note at `notes/<task-id>-<short-name>.md`.

Verify your local archive with `python project.py verify-release --exact-archive <archive>`. For the core ELF report, use `python -m tools.release_inventory <archive> --output local-output/core.json`. Record the exact command, engine SHA-256, tool version, and result. Keep APKs, libraries, private inputs, and raw binary dumps local.

For a mechanics note, record the setup, repeat each offline test, and vary one input at a time. Report measurements, units, precision, and uncertainty. Give provisional names to observed quantities when needed and label them **Inferred** with the evidence. Label unresolved questions **Unknown**.

Run `python project.py check` before submitting. The owner reviews the evidence and updates the task status. GitHub Actions publishes the dashboard and can report newly verified observations to Discord.
