# Prompt Archive

This folder stores reusable and historical Codex prompts that were used to plan, implement, review, and document platform subsystems.

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
