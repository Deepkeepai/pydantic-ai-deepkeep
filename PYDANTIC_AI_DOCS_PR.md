# Pydantic AI Docs PR

## Title

```text
[docs] Add DeepKeep AI Firewall to third-party guardrail capabilities
```

## Target file

```text
docs/capabilities/third-party.md
```

## Suggested diff

Add this bullet under `## Guardrails & Safety {#guardrails-safety}` after `pydantic-ai-shields`:

```markdown
* [`pydantic-ai-deepkeep`](https://github.com/Deepkeepai/pydantic-ai-deepkeep) - DeepKeep AI Firewall guardrails for Pydantic AI. Provides `DeepKeepGuardrail`, a custom capability that runs DeepKeep pre-moderation before model requests and post-moderation after model responses. Supports allow, block, redact, modify, and alert workflows for prompt injection, jailbreaks, sensitive data leakage, unsafe content, and other AI risks.
```

## PR body

```markdown
Adds DeepKeep AI Firewall to the Third-Party Capabilities page under Guardrails & Safety.

DeepKeep is distributed as an external `pydantic-ai-deepkeep` package and uses Pydantic AI's capability extension point, so this is a docs-only ecosystem listing and does not add vendor-specific code to Pydantic AI core.

Integration surface:

* `DeepKeepGuardrail` custom capability
* pre-model checks before model requests
* post-model checks after model responses
* support for allow, block, redact, modify, and alert guardrail actions
```

## Pre-submit checklist

* Public repository exists at `https://github.com/Deepkeepai/pydantic-ai-deepkeep`.
* Package is published or at least installable from the public repository.
* README includes Pydantic AI usage examples.
* Tests cover DeepKeep decision parsing, API payloads, and capability hook behavior.
* PR is docs-only and does not request core changes.
