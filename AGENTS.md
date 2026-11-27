# Contributor agents

Read README.md. For function matching, open the **Request one ARM64 function** issue form and wait for the assignment comment. The queue gives one function per GitHub account, with one account assigned per function. For documentation or verification tasks, choose one open ID from tasks.json and use the research claim form. Link your claim in the PR and use a separate branch or worktree.

For game-baseline work, use the shared archive in README.md and run `python project.py verify-release --exact-archive <archive>`. Keep it local. Record the baseline SHA-256, tool version, exact command, and result. Never add game APKs, assets, disassembly, memory dumps, profiles, tokens, or server addresses. The repository scope is verification tooling and documented observations. For an exact build match, use code the contributor owns or has permission to rebuild.

Run `python project.py check` before submitting. Contributors may propose results. A maintainer records separate reproduction, reviewer credit and an evidence URL before marking a task verified. A passing CI run is reproducibility evidence. Community PRs should also receive maintainer review. Keep the task ID stable and do not edit another contributor's task in an unrelated pull request.

For function matching, follow the assignment's `TASK.md` and [shared toolchain](TOOLCHAIN.md). Run `python tools/verify_fixture.py --fixture fixtures/<name>`. Submit `candidate.cpp` and test evidence. Keep the reference, hashes, size, compiler and flags, and negative control intact. A maintainer records the match date and evidence after review, which updates the dashboard and triggers the optional Discord notification. Close your claim when finished or to release it. Open a new request for the next function.
