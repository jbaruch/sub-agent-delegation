# Multi-Region Data Processing Pipeline: Agent Architecture Design

## Problem/Feature Description

A fintech company is building a multi-agent data processing system where an orchestrator spawns several specialized sub-agents: one to validate transaction records, one to detect anomalies, and one to produce compliance summaries. All three sub-agents need access to the same baseline configuration — the company's regulatory jurisdiction codes, data retention policy constants, and the internal API base URL for their compliance reporting service.

Previously a developer set this up and found that sub-agents were inconsistently configured: sometimes they operated with the right baseline configuration, sometimes without — with no error to indicate which was happening. After some debugging, the team discovered the sub-agents weren't reliably receiving the shared configuration. The developer wants a clean, production-grade redesign that solves this problem durably.

An additional complexity: a colleague suggested using a particular Agent SDK parameter when spawning sub-agents to "clone the parent session" so each sub-agent would automatically receive everything the parent has. The team wants the architecture decision documented clearly, including whether this approach is actually correct and what the parameter really does under the hood.

Finally, the sub-agents must be fully autonomous — they cannot pause mid-task to ask the orchestrator or a human operator for clarification. Any information they might need must be provided upfront in their configuration.

## Output Specification

Produce the following files:

1. A configuration file that stores shared baseline configuration values in the appropriate location so all sub-agents can reliably access them. Use the sample configuration values from the Input Files section below.

2. `orchestrator.py` — a Python orchestrator script that:
   - Launches three sub-agents (validator, anomaly_detector, compliance_reporter) using the Agent SDK
   - Shows how each sub-agent receives the skills and context it needs
   - Implements appropriate validation to detect when a sub-agent has not received its expected skills

3. `architecture_decision.md` — a short document (bullet points are fine) that explains:
   - Where shared cross-cutting configuration is stored and why that location was chosen
   - The team's decision on the colleague's suggestion about cloning parent session state into sub-agents, including a clear explanation of what that SDK parameter actually does
   - How the system handles the case where a sub-agent is missing expected context

## Input Files

The following files are provided as inputs. Extract them before beginning.

=============== FILE: inputs/baseline_config.txt ===============
REGULATORY_JURISDICTIONS=US-SEC,EU-MiFID2,UK-FCA
DATA_RETENTION_DAYS=2555
COMPLIANCE_API_BASE_URL=https://compliance-internal.fintech-corp.example.com/v3
ANOMALY_THRESHOLD_SIGMA=3.5
REPORT_FORMAT=json-ld
DEFAULT_CURRENCY=USD
=============== END FILE ===============
