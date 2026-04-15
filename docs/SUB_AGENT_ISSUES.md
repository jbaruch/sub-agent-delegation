# Sub-Agent Issues — Extended Gotcha List

The main `SKILL.md` calls out the single most dangerous gotcha (the `context: fork`
semantic inversion). The issues below are additional papercuts and documentation bugs
that a sub-agent orchestrator should be aware of.

## 1. `context: fork` is semantically inverted

`fork` creates an **ISOLATED blank context**, not a copy of the parent. If you rely on
the English meaning you will ship a broken orchestrator.

- GitHub issue: [anthropics/claude-code#20492](https://github.com/anthropics/claude-code/issues/20492)

## 2. `AskUserQuestion` is silently unavailable in sub-agents

The tool is listed as available but calls fail or return empty. Sub-agents that rely on
human-in-the-loop clarification will freeze or loop.

- GitHub issue: [anthropics/claude-code#34592](https://github.com/anthropics/claude-code/issues/34592)

## 3. Sub-agents silently default to a different model than the parent

If you do not pin `model` in the `AgentDefinition`, the sub-agent may run on a
different (often weaker) model. Symptoms look like a capability regression that turns
out to be a routing regression.

- GitHub issue: [anthropics/claude-code#5456](https://github.com/anthropics/claude-code/issues/5456)

## 4. Filesystem skill discovery bypass

Sub-agents can currently pick up skills directly from `.claude/skills/` on disk, but
the documentation says they can't. This works today, may break tomorrow, and should
not be used as a production channel for passing skills.

- GitHub issue: [anthropics/claude-code#32910](https://github.com/anthropics/claude-code/issues/32910)

## 5. Parent-context inheritance (feature request, still OPEN)

17 upvotes as of writing. Until this lands, every sub-agent starts fully blank except
for `CLAUDE.md`, tools, and MCP servers — which is the premise of this whole skill.

- GitHub issue: [anthropics/claude-code#12790](https://github.com/anthropics/claude-code/issues/12790)

## 6. Silent billing routing to a pricier model

Some sub-agent invocations have been observed routing through higher-priced models
without warning, producing unexpectedly large bills.

- GitHub issue: [anthropics/claude-code#39903](https://github.com/anthropics/claude-code/issues/39903)

---

These references back the core `SKILL.md`. If you close any of the above tracking
issues with resolutions that change the inheritance model, also update the skill body
so future orchestrators don't act on stale assumptions.
