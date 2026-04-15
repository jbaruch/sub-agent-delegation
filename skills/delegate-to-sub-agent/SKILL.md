---
name: delegate-to-sub-agent
description: Orchestrate Claude sub-agents correctly. Use when spawning child agents, delegating tasks to another agent, building multi-agent pipelines, or troubleshooting why a sub-agent doesn't have access to expected skills or context. Covers what inherits (CLAUDE.md, tools, MCP) vs what doesn't (skills, history, system prompt, state), how to pass skills explicitly via AgentDefinition or inline prompt, and how to validate the handoff with a skills-echo protocol.
---

# Sub-Agent Delegation

Sub-agents do **not** inherit the orchestrator's skills, history, or accumulated state.
They start with a blank slate. The only inheritance you can rely on is:

- `CLAUDE.md` content
- Tool definitions (all, unless you restrict them)
- MCP servers (all — there is no per-sub-agent scoping today)

Everything else — including skills under `.claude/skills/` — is **opt-in** per sub-agent
and must be passed explicitly.

## The two channels

1. **Agent SDK (`AgentDefinition`)**
   - Pass skills by name: `AgentDefinition(skills=["govee-h6056", "face-recognition-calibration"])`
   - Preferred when you control the launcher.
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
   - You cannot attach a skills list to the tool call.
   - Inline the skill content directly in the prompt string.
   - Filesystem discovery of `.claude/skills/` technically works but is undocumented
     (GH #32910) and should not be relied on.
   - Inline example:
     ```
     <skill name="govee-h6056">
     # Govee H6056 skill content here …
     </skill>

     Your task is: adjust the living-room lights to 50 % brightness.
     First, echo back the skill names you received.
     ```

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
