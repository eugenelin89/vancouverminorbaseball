# Prompt Archive

This folder stores reusable and historical Codex prompts that were used to plan, implement, review, and document platform subsystems.

Prompt bodies may mention paths or phase status that were true at the time the prompt was used. Treat them as historical execution records unless a current task explicitly says to reuse one.

Prompts are stored directly in this folder using this filename format:

```text
prompt_[ID]_[app_name].md
```

Current app/subsystem names:

- `analytics`
- `account_management`
- `platform`

Use the next unused integer ID when creating a new prompt. Keep IDs zero-padded for sorting, and do not rename existing prompt files after they are created unless reorganizing the archive deliberately.

These prompts are useful historical context, but they are not the canonical architecture source. Current architecture and subsystem guidance lives in:

- [Platform Architecture](../ARCHITECTURE.md)
- [Analytics Documentation](../analytics/README.md)
- [Account Management V1 Summary](../account_management/V1_SUMMARY.md)

When creating new prompts, use the app/subsystem name that the prompt primarily affects. If a prompt spans multiple subsystems, use `platform`.

## Prompt Records For File-Changing Tasks

When a user prompt creates, modifies, moves, or deletes files, create a prompt record in this folder.

The prompt record should include:

- the user's prompt;
- the app/subsystem name used for the filename;
- the commit hash for the resulting work commit;
- the diff of that work commit against the previous commit.

The normal workflow is:

1. Complete the requested file changes.
2. Update `project_flat_file.txt`.
3. Commit the requested work with a concise message based on the work completed.
4. Generate the commit diff.
5. Add the diff to the prompt record.
6. Update `project_flat_file.txt` again.
7. Commit the prompt record separately.

Do not include unrelated user changes in either commit.
