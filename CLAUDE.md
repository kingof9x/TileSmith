# Claude Code notes

## Secrets in commands

Commands approved with "Yes, and don't ask again" are saved word for word in
`.claude/settings.local.json`, including any password, API key or token in them.

- Never put a password, API key or token directly in a command. Read it from an
  environment variable (e.g. `$API_TOKEN`) or a file that git ignores instead.
- If a command can't avoid containing a secret, stop and warn me before running
  it, and remind me not to choose "don't ask again" for it.
- Never commit `.claude/settings.local.json` (it is in `.gitignore`).
