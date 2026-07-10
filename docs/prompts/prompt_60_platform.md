# Prompt 60 - Platform

## User Prompt

```text
can you add a rule so that you don't need to ask me for permission and just execute every git command
```

## Resulting Commit

```text
f125ab1 Update git command workflow policy
```

## Commit Diff

```diff
commit f125ab1c327531a02942bdade537ecd0841abb68
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Fri Jul 10 10:52:17 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Fri Jul 10 10:52:17 2026 -0700

    Update git command workflow policy
---
 AGENTS.md | 2 ++
 1 file changed, 2 insertions(+)

diff --git a/AGENTS.md b/AGENTS.md
index 88671c3..7811510 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -44,6 +44,8 @@ When a user prompt causes any file to be created, modified, moved, or deleted:
 - Push the resulting commits to the remote repository before finishing the workflow.
 - Do not include unrelated user changes in either commit.
 - If a task cannot be committed safely because the worktree contains unrelated staged changes or an instruction explicitly forbids committing, explain the blocker.
+- Execute routine git commands directly as part of this workflow without asking the user for additional conversational permission, including `git status`, `git diff`, `git add`, `git commit`, `git log`, and `git push`.
+- This rule does not override tool-enforced approval prompts or safety restrictions. If the execution environment requires approval for a git command, request that approval through the tool rather than asking separately in chat.
 
 ## Architecture Boundaries
```
