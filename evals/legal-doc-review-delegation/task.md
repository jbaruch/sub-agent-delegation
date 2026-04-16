# Document Analysis Pipeline: Claude Code Task Tool Integration

## Problem/Feature Description

A legal-tech firm uses Claude Code as their primary automation layer. They want to build a document-review workflow where a coordinator agent dispatches individual contract sections to specialized reviewer sub-agents. The firm already has a `contract-risk-analyzer` skill with detailed guidance on how to flag liability clauses, indemnification issues, and termination conditions.

The engineering constraint is that this workflow must use the Claude Code Task tool (not the Agent SDK) because it needs to fit inside their existing Claude Code session automation scripts. Their previous attempt at a similar pipeline failed intermittently — sometimes the sub-agent produced high-quality reviews and sometimes it behaved as if it had no specialized guidance at all, with no error to explain the difference.

The team wants a reliable, debuggable implementation that surfaces handoff failures immediately rather than silently producing inconsistent output.

## Output Specification

Write a Python script `document_pipeline.py` that:

1. Defines a function `build_task_prompt(skill_content: str, section_text: str) -> str` that takes the raw text of the `contract-risk-analyzer` skill and a contract section, and returns a complete prompt string ready to pass to the Task tool. The prompt must include both the skill content and the contract section, and must set the sub-agent up to confirm what skills it received before beginning its analysis.

2. Defines a function `dispatch_review(skill_content: str, section_text: str) -> str` that calls `build_task_prompt`, simulates dispatching it via the Task tool (you can stub the actual tool call with a local function `mock_task_tool(prompt: str) -> str` that returns a realistic-looking sub-agent first-response), parses the sub-agent's first response to validate that the skill handoff succeeded, and returns the analysis. If validation fails, it must raise an error immediately with details about what was expected versus what was received.

3. Includes a `main()` block that runs `dispatch_review` with a sample skill content string and sample contract section, prints the result, and also prints a confirmation that the skill handoff was validated.

Also write a `pipeline_design.md` that explains the approach taken to pass skills through the Task tool and why this approach was chosen over alternatives.

## Input Files

The following files are provided as inputs. Extract them before beginning.

=============== FILE: inputs/sample_contract_section.txt ===============
SECTION 12 — LIMITATION OF LIABILITY

In no event shall either Party be liable to the other for any indirect, incidental,
special, exemplary, or consequential damages (including, but not limited to, procurement
of substitute goods or services; loss of use, data, or profits; or business interruption)
however caused and on any theory of liability, whether in contract, strict liability,
or tort (including negligence or otherwise) arising in any way out of the use of the
Services, even if advised of the possibility of such damage.

The aggregate liability of either Party under this Agreement shall not exceed the total
fees paid or payable by Customer to Provider in the twelve (12) months preceding the
claim. This limitation shall apply notwithstanding any failure of essential purpose of
any limited remedy.

Neither Party shall have any obligation to indemnify the other Party for third-party
claims arising from acts or omissions of that other Party's contractors or agents.
=============== END FILE ===============
