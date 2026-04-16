# Sub-Agent Delegation Rules

**Platform-agnostic.** The context-loss problem is the same on Claude Code and Copilot.

## The universal rule

- **Sub-agents / extensions / participants start with FRESH context.** They do NOT inherit parent's skills, history, or accumulated state.
- **Pass skills explicitly** — every platform, every time.
- **Validate the handoff.** First sub-agent action: echo received skills. Fail loudly on mismatch.

## Claude Code

- Inherit: `CLAUDE.md`, tool definitions, MCP servers.
- Pass skills: `AgentDefinition(skills=[...])` or inline in Task tool prompt.
- `context: fork` is INVERTED (GH #20492) — creates blank, not copy.
- `AskUserQuestion` unavailable in sub-agents (GH #34592).

## GitHub Copilot

- Inherit: workspace context (`@workspace`), `#file`/`#selection` references, participant's system prompt.
- Pass skills: inline in extension system prompt or `#file:path/to/skill.md`.
- Copilot Extensions (GitHub Apps) get FRESH context per request — same as Claude sub-agents.
- Agent mode persists within session BUT delegates to tools/extensions with fresh context.

## Cross-platform ground truth

| | Claude Code | Copilot |
|---|---|---|
| Shared context | `CLAUDE.md` | `.github/copilot-instructions.md` |
| Skill passing | `AgentDefinition(skills=[...])` | inline or `#file` refs |
| Handshake | echo-skills protocol | same pattern works |
