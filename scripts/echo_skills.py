"""
Validation helpers for sub-agent skill handoff.

Usage in the orchestrator:

    expected = ["govee-h6056", "face-recognition-calibration"]
    preamble = build_echo_preamble(expected)
    prompt = preamble + "\n\n" + actual_task_prompt
    result = launch_sub_agent(prompt=prompt, ...)
    assert_echo_matches(result.first_message, expected)

The echo protocol forces the sub-agent to reveal which skills it actually received
as its very first action, so the orchestrator can fail loudly on missing context
instead of letting the sub-agent operate silently under-informed.
"""

from __future__ import annotations

import re
from typing import Iterable


ECHO_PREFIX = "SKILLS_ECHO:"
ECHO_PATTERN = re.compile(rf"^{re.escape(ECHO_PREFIX)}\s*(?P<skills>.+)$", re.MULTILINE)


def build_echo_preamble(expected_skills: Iterable[str]) -> str:
    """Prompt preamble that instructs the sub-agent to echo its skills first."""
    names = sorted({s.strip() for s in expected_skills if s.strip()})
    listed = ", ".join(names) if names else "(none)"
    return (
        "Before doing anything else, reply with a single line in this exact form:\n"
        f"    {ECHO_PREFIX} <comma-separated list of skill names you can see>\n"
        f"The orchestrator expects: {listed}.\n"
        "If the list does not match, stop and say 'MISSING SKILLS' — do not attempt the task.\n"
    )


def parse_echo(message: str) -> list[str] | None:
    """Extract the echoed skill names from the sub-agent's first message."""
    match = ECHO_PATTERN.search(message or "")
    if not match:
        return None
    raw = match.group("skills").strip()
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


def assert_echo_matches(message: str, expected_skills: Iterable[str]) -> None:
    """Raise if the sub-agent's echo doesn't match the expected skill set."""
    echoed = parse_echo(message)
    expected = sorted({s.strip() for s in expected_skills if s.strip()})
    if echoed is None:
        raise RuntimeError(
            "Sub-agent did not produce a SKILLS_ECHO line. Handoff probably failed."
        )
    actual = sorted(echoed)
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise RuntimeError(
            f"Sub-agent skill mismatch. missing={missing} extra={extra} "
            f"actual={actual} expected={expected}"
        )


if __name__ == "__main__":
    # Quick self-check
    expected = ["govee-h6056", "face-recognition-calibration"]
    preamble = build_echo_preamble(expected)
    print("PREAMBLE:\n", preamble)
    good = "SKILLS_ECHO: govee-h6056, face-recognition-calibration\n...rest..."
    bad = "SKILLS_ECHO: govee-h6056\n...rest..."
    assert_echo_matches(good, expected)
    print("good message validated")
    try:
        assert_echo_matches(bad, expected)
    except RuntimeError as exc:
        print("bad message correctly rejected:", exc)
