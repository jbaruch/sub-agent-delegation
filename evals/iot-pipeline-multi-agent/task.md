# Smart Home Pipeline: Lighting Orchestrator

## Problem/Feature Description

A home-automation startup is building a Python orchestration layer that coordinates specialized sub-agents to control different smart home devices. The platform already has two skills registered in `.claude/skills/`: `govee-h6056` for their LED strip lighting system and `face-recognition-calibration` for presence detection. The orchestrator's job is to detect whether someone is in a room (via the face recognition skill) and then adjust the lighting accordingly (via the govee skill).

The engineering team has found that sub-agents frequently fail silently — they run but produce garbage output because they lack the context they need. The team wants a robust orchestrator that catches these failures at startup rather than discovering them after the lights have been set incorrectly for 20 minutes.

## Output Specification

Write a Python script `orchestrator.py` that:

1. Defines a function `build_lighting_pipeline()` that creates and returns a sub-agent capable of handling both face recognition and lighting control. The sub-agent should be set up with the skills it needs to perform both tasks.
2. Defines a function `run_pipeline(task_prompt: str) -> str` that launches the sub-agent with a given task prompt, validates that the sub-agent received its expected skills before proceeding, and returns the sub-agent's response. If the skill handoff fails, the function should raise a descriptive error immediately.
3. Includes a `main()` block that calls `run_pipeline` with the example prompt: `"Is anyone in the living room? If yes, set the lights to a warm 40% brightness."` and prints the result.

The script should be written so that another engineer reading it can immediately see which skills are being passed, how the handoff is validated, and what happens when something goes wrong.

Sub-agents must be fully autonomous with no human-in-the-loop — they should never call AskUserQuestion or pause for clarification.

Also produce a short `design_notes.md` that explains: (a) what context a sub-agent does and does not automatically receive from its parent, and (b) how the orchestrator handles the case where the sub-agent doesn't receive the expected skills.
