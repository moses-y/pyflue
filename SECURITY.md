# Security Policy

PyFlue includes sandbox tools that can read files, write files, and run shell
commands when explicitly enabled. Treat any agent with write or shell access as
privileged code.

## Supported Versions

Security fixes target the latest released version.

## Reporting a Vulnerability

Please report security issues privately to:

```text
hello@super-agentic.ai
```

Do not open a public issue for a suspected vulnerability.

## Sandbox Guidance

- Keep `allow_write` disabled unless the workflow needs file writes.
- Keep `allow_shell` disabled unless the workflow needs shell execution.
- Prefer command allowlists for production agents.
- Do not pass secrets into prompts or Markdown skills.
- Use environment variables or provider-specific secret mechanisms for tokens.
