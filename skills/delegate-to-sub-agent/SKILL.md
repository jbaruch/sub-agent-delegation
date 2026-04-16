---
name: delegate-to-sub-agent
description: Orchestrate sub-agents across Claude Code AND GitHub Copilot. Covers what inherits vs what doesn't on each platform, how to pass skills explicitly, and the echo-skills validation handshake. Use when spawning child agents, delegating tasks, building multi-agent pipelines, or troubleshooting why a sub-agent doesn't have access to expected skills or context.
---

# Sub-Agent Delegation

Sub-agents do **not** inherit the orchestrator's skills, history, or accumulated state
on ANY platform. They start with a blank slate. The core problem is the same whether
you're on Claude Code or GitHub Copilot: **delegation is a context-loss event unless
you explicitly propagate what the sub-agent needs.**

## Claude Code inheritance model

What Claude sub-agents DO inherit:
- `CLAUDE.md` content
- Tool definitions (all, unless you restrict them)
- MCP servers (all — there is no per-sub-agent scoping today)

What they do NOT inherit:
- Skills (unless explicitly listed in `AgentDefinition`)
- Parent conversation history
- Parent system prompt
- Accumulated state

### Claude Code channels

1. **Agent SDK (`AgentDefinition`)**
   - Pass skills by name: `AgentDefinition(skills=["govee-h6056", "face-recognition-calibration"])`
   - Complete example:
     ```python
     agent = AgentDefinition(
         model="claude-opus-4-5",
         skills=["govee-h6056", "face-recognition-calibration"],
         system_prompt="You are a lighting-control specialist.",
     )
     result = agent.run(task_prompt)
     ```

2. **Claude Code Task tool**
   - Cannot attach a skills list to the tool call.
   - Inline the skill content directly in the prompt string.
   - Filesystem discovery of `.claude/skills/` technically works but is undocumented
     (GH #32910) — do not rely on it.

## GitHub Copilot inheritance model

Copilot's multi-agent architecture uses **participants** and **extensions** instead
of sub-agents, but the context-loss problem is the same.

What Copilot agents/participants DO inherit:
- The VS Code workspace context (`@workspace`)
- Files explicitly referenced via `#file`, `#selection`, `#editor` context variables
- The participant's own registered system prompt

What they do NOT inherit:
- Other participants' accumulated state
- Skills/instructions from the parent conversation (unless re-injected)
- `.github/copilot-instructions.md` is workspace-level (like `CLAUDE.md`) but
  does NOT propagate into Copilot Extensions running as separate GitHub Apps

### Copilot channels

1. **Copilot Extensions (GitHub Apps)**
   - Each extension is a standalone agent with its own system prompt.
   - Context arrives via the API request payload — NOT inherited from the user's
     VS Code session.
   - Pass skills by inlining them in the extension's system prompt or in the
     user message routed to the extension.

2. **Copilot Chat Participants (VS Code API)**
   - Register via `vscode.chat.createChatParticipant()`.
   - Each participant gets the user's message + explicitly referenced context
     (`#file`, `#selection`), NOT the full conversation history with other participants.
   - Pass skills by referencing files (`#file:path/to/skill.md`) or by inlining
     in the participant's `handleRequest` system prompt.

3. **Copilot Agent Mode (VS Code)**
   - The agent maintains conversation context WITHIN a single session (unlike
     Claude sub-agents which start fresh per spawn).
   - BUT: when agent mode delegates to a tool or extension, that tool/extension
     gets a fresh context — same problem as Claude.

### Cross-platform ground truth

| Concern | Claude Code | GitHub Copilot |
|---|---|---|
| Workspace-level shared context | `CLAUDE.md` | `.github/copilot-instructions.md` |
| Per-agent skill passing | `AgentDefinition(skills=[...])` | inline in system prompt or `#file` references |
| Conversation persistence | Sub-agents start FRESH | Agent mode persists, but extensions are fresh |
| Validation handshake | Echo-skills protocol (below) | Same pattern works — add to system prompt |

## Validation protocol

Every sub-agent's **first action** must be to echo back the skill names it received.
The orchestrator verifies the echo matches the expected set. If it doesn't, fail
loudly rather than letting the sub-agent operate with missing context.

Minimal echo handler (inline in the sub-agent preamble or in [`scripts/echo_skills.py`](../../scripts/echo_skills.py)):

```python
import json, sys

def echo_skills(received: list[str], expected: list[str]) -> None:
    missing = set(expected) - set(received)
    extra   = set(received)  - set(expected)
    if missing or extra:
        raise RuntimeError(
            f"Skill handoff mismatch — missing: {missing}, unexpected: {extra}"
        )
    print(json.dumps({"skills_echo": received}), flush=True)

echo_skills(
    received=["govee-h6056", "face-recognition-calibration"],
    expected=["govee-h6056", "face-recognition-calibration"],
)
```

The orchestrator parses the `skills_echo` JSON line from the sub-agent's first
output and aborts the run if the lists don't match.

## Cross-sub-agent ground truth

If a piece of information must reach **every** sub-agent, put it in `CLAUDE.md`.
Skills are opt-in per sub-agent and will otherwise silently not apply.

## Critical gotcha

- **`context: fork` is semantically inverted** — it creates an ISOLATED blank context,
  not a fork of the parent. → [GH #20492](https://github.com/anthropics/claude-code/issues/20492)

For additional known issues (silent model switching, AskUserQuestion unavailability,
billing routing, filesystem skill discovery), see [../../docs/SUB_AGENT_ISSUES.md](../../docs/SUB_AGENT_ISSUES.md).

## How to act

1. Before launching a sub-agent, list the exact skills it needs.
2. Use `AgentDefinition(skills=[...])` if you're on the SDK. Otherwise, inline the
   skill bodies into the prompt string.
3. Include the echo-skills preamble so the first sub-agent response lets you verify
   the handoff; abort loudly if the echo doesn't match.
4. If cross-cutting context is required, put it in `CLAUDE.md` — do not rely on
   implicit inheritance.

See the rule `sub-agent-delegation-rules` for a quick reminder card.
