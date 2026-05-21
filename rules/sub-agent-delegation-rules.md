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

## VS Code Copilot

- Agent mode persists within session BUT terminal commands and chat participants get fresh context.
- Scripts the agent writes that spawn sub-processes inherit NOTHING from Copilot.
- Pass skills: `#file:path/to/SKILL.md` in chat, or `.github/copilot-instructions.md` for always-on.

## Koog (Kotlin/JVM) — no native skill registry

Koog 1.0.0-preview3's `AIAgent(...)` factory only takes a `systemPrompt`. There is no `skills=[...]` parameter. Native skill support is tracked at [JetBrains/koog#1383](https://github.com/JetBrains/koog/issues/1383).

**Fallback while the native API is missing: read the installed skill files and inject their content into the sub-agent's `systemPrompt` at agent-creation time.** Do NOT copy-paste skill content into your source — drift between the plugin repo and your code turns the demo's "skill handoff" beat into theatre.

```kotlin
private fun readSkillRules(pluginName: String): String {
    val tileDir = listOf(
        File(".tessl/tiles/jbaruch/$pluginName"),
        File("../../.tessl/tiles/jbaruch/$pluginName")
    ).firstOrNull { it.isDirectory }
        ?: error("Run `tessl install jbaruch/$pluginName` before invoking this sub-agent.")
    return File(tileDir, "rules").listFiles { f -> f.extension == "md" }
        ?.sortedBy { it.name }
        ?.joinToString("\n\n---\n\n") { it.readText() } ?: ""
}

val visionAgent = AIAgent(
    promptExecutor = PromptExecutor.builder().anthropic(apiKey).build(),
    llmModel = AnthropicModels.Sonnet_4,
    strategy = functionalStrategy<String, String> { input ->
        requestLLM(input).parts.filterIsInstance<MessagePart.Text>().joinToString("\n") { it.text }
    },
    systemPrompt = """
        You are the vision sub-agent.

        SKILL (jbaruch/face-recognition-calibration-djl):
        ${readSkillRules("face-recognition-calibration-djl")}

        ... task description ...
    """.trimIndent()
)
```

When Koog ships native skills (koog#1383), swap `readSkillRules(...)` for the native registration call. The same fallback pattern applies to any framework where sub-agents only accept a system prompt.

## Cross-platform ground truth

| | Claude Code | VS Code Copilot | Koog (Kotlin/JVM) |
|---|---|---|---|
| Shared context | `CLAUDE.md` | `.github/copilot-instructions.md` | `CLAUDE.md` / `AGENTS.md` |
| Per-request skills | `AgentDefinition(skills=[...])` | `#file:path/to/SKILL.md` | inject `readSkillRules(...)` into `systemPrompt` until [koog#1383](https://github.com/JetBrains/koog/issues/1383) |
| Subprocess context | Sub-agents start FRESH | Terminal commands are bare | `AIAgent.run()` starts FRESH |
| Handshake | echo-skills protocol | same pattern works | same pattern works |
