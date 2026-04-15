# Sub-Agent Delegation Rules

When launching a Claude sub-agent:

- **Sub-agents start with FRESH context.** They do NOT inherit:
  - parent's conversation history
  - parent's system prompt
  - parent's accumulated state
  - **skills** (unless listed explicitly)
- They DO inherit: `CLAUDE.md`, tool definitions, MCP servers.
- **Pass skills explicitly:**
  - Agent SDK → `AgentDefinition(skills=[...])`
  - Task tool → inline the skill body in the prompt string.
- **Validate the handoff.** First sub-agent action: echo the skills it received. Fail loudly on mismatch.
- **Cross-cutting ground truth → `CLAUDE.md`.** Everything else is opt-in.

Known gotchas: `context: fork` is inverted (GH #20492), `AskUserQuestion` unavailable in sub-agents (GH #34592), model default silent switch (GH #5456), filesystem skill discovery undocumented (GH #32910), parent-context inheritance still open (GH #12790), silent billing routing (GH #39903).

Reference: `skills/delegate-to-sub-agent/SKILL.md` and `scripts/echo_skills.py`.
