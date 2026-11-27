# Contributor agents

Read README.md and choose one open task from tasks.json. In the shared repository, claim its ID in one issue before editing and link the issue from the pull request. Use a separate branch or worktree for each task. Keep results small enough for another contributor to reproduce.

For game-baseline work, use the shared archive in README.md and run `python project.py verify-release --exact-archive <archive>`. Keep it local. Record the baseline SHA-256, tool version, exact command, and result. Never add game APKs, assets, disassembly, memory dumps, profiles, tokens, or server addresses. The repository scope is verification tooling and documented observations. For an exact build match, use code the contributor owns or has permission to rebuild.

Run `python project.py check` before submitting. Contributors may propose results. A maintainer records separate reproduction, reviewer credit and an evidence URL before marking a task verified. A passing CI run is reproducibility evidence. Community PRs should also receive maintainer review. Keep the task ID stable and do not edit another contributor's task in an unrelated pull request.
