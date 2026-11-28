# Contributor agents

Read README.md. For function matching, choose any open ID from `function_catalog.json` or the dashboard. Multiple contributors may work on the same ID. For documentation or verification tasks, choose an open ID from `tasks.json` and use the research claim form. Link that claim in the research PR. Work in a separate branch, fork or worktree.

For game-baseline work, use the shared archive in README.md and run `python project.py verify-release --exact-archive <archive>`. Keep it local. Record the baseline SHA-256, tool version, exact command, and result. Never add game APKs, assets, disassembly, memory dumps, profiles, tokens, or server addresses. The repository scope is verification tooling and documented observations. For an exact build match, use code the contributor owns or has permission to rebuild.

Run `python project.py check` before submitting. Contributors may propose results. A maintainer records separate reproduction, reviewer credit and an evidence URL before marking a task verified. A passing CI run is reproducibility evidence. Community PRs should also receive maintainer review. Keep the task ID stable and do not edit another contributor's task in an unrelated pull request.

For function matching, follow the fixture's `TASK.md` and the [shared toolchain](TOOLCHAIN.md). Run `python -m tools.verify_fixture --function HCR2-NNN` with the chosen ID. Open a PR titled `[HCR2-NNN] Match <symbol>`. Change only that fixture's `candidate.cpp` and paste its `match.json` path, verification command and `MATCH` line in the PR body. The line identifies the ELF symbol, section, byte count and SHA-256. Leave the locked reference, build settings, negative control and catalog alone. The repository owner records accepted matches in a separate change.
