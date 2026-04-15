# sub-agent-delegation

A [Tessl](https://tessl.io) **meta-plugin** for orchestrating Claude sub-agents
correctly: what inherits, what does not, how to pass skills explicitly, and how to
validate the handoff.

## What this plugin provides

| Kind | Name | Purpose |
|---|---|---|
| Skill | `delegate-to-sub-agent` | Two delegation channels (Agent SDK and Task tool), inline examples, echo-validation protocol. |
| Rule  | `sub-agent-delegation-rules` | Concise in-context reminder card. |
| Script | `scripts/echo_skills.py` | Skills-echo preamble builder and validator. |
| Doc  | `docs/SUB_AGENT_ISSUES.md` | Extended list of documented sub-agent gotchas with GitHub issue links. |

## Why it exists

Claude sub-agents start with a **fresh context**. They inherit:

- `CLAUDE.md`
- Tool definitions (all, unless restricted)
- MCP servers (all — no per-sub-agent scoping yet)

They do **not** inherit:

- Parent conversation history
- Parent system prompt
- Accumulated state
- **Skills** (unless listed explicitly)

That last one bites orchestrators who assume a sub-agent will see the same skills the
parent can see. It won't. This plugin encodes the explicit-passing pattern and a
validation handshake that fails loudly if the handoff is wrong.

## Install

```bash
tessl install jbaruch/sub-agent-delegation
```

Or from this repo:

```bash
tessl install github:jbaruch/sub-agent-delegation
```

## Usage (quick)

```python
from scripts.echo_skills import build_echo_preamble, assert_echo_matches

expected = ["govee-h6056", "face-recognition-calibration"]
preamble = build_echo_preamble(expected)
prompt   = preamble + "\n\n" + actual_task_prompt

# launch sub-agent with `prompt` ...
assert_echo_matches(first_message_from_sub_agent, expected)
```

See `skills/delegate-to-sub-agent/SKILL.md` for the full playbook,
`rules/sub-agent-delegation-rules.md` for the short version, and
`docs/SUB_AGENT_ISSUES.md` for the extended gotcha list.

## License

MIT — see `LICENSE`.
