# Contributor agents

Read README.md and choose one open task from tasks.json. In the shared repository, claim its ID in one issue before editing and link the issue from the pull request. Use a separate branch or worktree for each task. Keep results small enough for another contributor to reproduce.

Use only local, lawfully obtained inputs and synthetic fixtures. Record the baseline SHA-256, tool version, exact command, and result. Never add game APKs, assets, disassembly, memory dumps, profiles, tokens, or server addresses. The repository scope is verification tooling and documented observations. For an exact build match, use code the contributor owns or has permission to rebuild.

Run `python project.py dashboard` after changing the task registry. Contributors may propose results. A maintainer marks a task verified after a second person reproduces the result and records their name and a link to review evidence. Keep the task ID stable and do not edit another contributor's task in an unrelated pull request.
