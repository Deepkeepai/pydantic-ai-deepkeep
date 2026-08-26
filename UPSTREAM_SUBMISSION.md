# Upstream submission notes

## Target

Ask Pydantic AI to list DeepKeep under integrations or custom capabilities as a custom guardrail integration named DeepKeep AI Firewall.

## Recommended listing

```text
DeepKeep AI Firewall
Use DeepKeep AI Firewall as a custom Pydantic AI capability to enforce runtime guardrails before model requests and after model responses. Supports allow, block, redact, modify, and alert workflows for prompt injection, jailbreaks, sensitive data leakage, unsafe content, and other AI risks.
```

## Integration surface

DeepKeep should be positioned as a custom capability, not a model provider, toolset, or observability backend.

Pydantic AI capabilities are reusable bundles of hooks, tools, instructions, and model settings. DeepKeep enforcement should run deterministically around model execution, so the correct extension points are `AbstractCapability.before_model_request` and `AbstractCapability.after_model_request`.

For application-only examples, Pydantic AI's `Hooks` capability can demonstrate the same idea. For an approved reusable integration listing, use a packaged `AbstractCapability` so users can install and compose `DeepKeepGuardrail` with other capabilities.

## Endpoint contract

The Pydantic AI package follows the same endpoints as `langchain-deepkeep`:

- `POST /api/v3/openai/moderations/pre`
- `POST /api/v3/openai/moderations/post`
- Header: `X-API-Key: <DEEPKEEP_API_KEY>`
- Pre payload: `{"model": "input-firewall-id", "input": "...", "title": "", "chat": ""}`
- Post payload: `{"model": "output-firewall-id", "output": "...", "title": "", "chat": ""}`

## Suggested Pydantic AI issue title

```text
[docs] List DeepKeep AI Firewall as a custom capability integration
```

## Suggested Pydantic AI PR title

```text
[docs] Add DeepKeep AI Firewall custom guardrails integration
```

## Maintainer-facing rationale

DeepKeep is distributed as an external package, so Pydantic AI core does not need to maintain vendor-specific API code. The integration uses Pydantic AI's documented `AbstractCapability` lifecycle hooks and can be listed as an approved custom guardrail integration once accepted by maintainers.

## Likely docs location

Pydantic AI already has `Third-Party Capabilities > Guardrails & Safety`. Add DeepKeep there, as a peer to `pydantic-ai-shields`.

Source file:

```text
docs/capabilities/third-party.md
```

No `docs/navigation.yml` change should be needed because this edits an existing page.

Suggested Markdown entry:

```markdown
- [`pydantic-ai-deepkeep`](https://github.com/Deepkeepai/pydantic-ai-deepkeep) - DeepKeep AI Firewall guardrails for Pydantic AI. Provides `DeepKeepGuardrail`, a custom capability that runs DeepKeep pre-moderation before model requests and post-moderation after model responses. Supports allow, block, redact, modify, and alert workflows for prompt injection, jailbreaks, sensitive data leakage, unsafe content, and other AI risks.
```

## PR checklist

- Publish `pydantic-ai-deepkeep` to PyPI first.
- Make the repository public under `Deepkeepai/pydantic-ai-deepkeep`.
- Include README examples for pre-model and post-model checks.
- Depend on `pydantic-ai-slim`, not the full `pydantic-ai` package with optional provider extras.
- Include mocked tests for decision parsing and hook behavior.
- Keep the Pydantic AI docs PR documentation-only.
- Avoid requesting Pydantic AI core changes unless maintainers ask for them.
