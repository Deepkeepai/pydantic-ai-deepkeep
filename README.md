# pydantic-ai-deepkeep

DeepKeep AI Firewall custom guardrails for Pydantic AI.

This package follows Pydantic AI's native custom capability extension point. Add `DeepKeepGuardrail` to an `Agent` with `capabilities=[...]` to check input before a model request and output after a model response.

## Installation

```bash
pip install pydantic-ai-deepkeep
```

Set credentials:

```bash
export DEEPKEEP_API_KEY="dk_..."
export DEEPKEEP_BASE_URL="https://api.example.deepkeep.ai"
```

## Input and output guardrails

```python
from pydantic_ai import Agent
from pydantic_ai_deepkeep import DeepKeepGuardrail

agent = Agent(
    "openai:gpt-5.2",
    instructions="Answer user questions safely and concisely.",
    capabilities=[
        DeepKeepGuardrail(
            pre_model="input-firewall-id",
            post_model="output-firewall-id",
        )
    ],
)

result = agent.run_sync("Explain how to store API keys securely.")
print(result.output)
```

## Agent specs

`DeepKeepGuardrail` supports Pydantic AI agent specs when registered as a custom capability type:

```yaml
model: openai:gpt-5.2
instructions: Answer user questions safely and concisely.
capabilities:
  - DeepKeepGuardrail:
      pre_model: input-firewall-id
      post_model: output-firewall-id
```

```python
from pydantic_ai import Agent
from pydantic_ai_deepkeep import DeepKeepGuardrail

agent = Agent.from_file("agent.yaml", custom_capability_types=[DeepKeepGuardrail])
```

## Why a capability

Pydantic AI capabilities bundle hooks, tools, instructions, and settings. DeepKeep should run deterministically around model execution, so the correct integration surface is a custom `AbstractCapability`, not an agent-callable tool.

`DeepKeepGuardrail` uses:

- `before_model_request` for DeepKeep pre-moderation before content reaches the model.
- `after_model_request` for DeepKeep post-moderation before model output is returned.

## DeepKeep endpoints

This package uses the same DeepKeep OpenAI-compatible moderation endpoints as the other DeepKeep integrations:

- `POST /api/v3/openai/moderations/pre` with `{"model", "input", "title", "chat"}`.
- `POST /api/v3/openai/moderations/post` with `{"model", "output", "title", "chat"}`.
- `X-API-Key` for authentication.

`pre_model` and `post_model` are DeepKeep firewall IDs. Each value is sent to the matching moderation endpoint as the `model` field.

## Guardrail actions

DeepKeep responses are interpreted from `verbosity[].details.guardrail_action`:

- `block`: Raises `DeepKeepBlockedError` and aborts the run.
- `redact` or `modify`: Replaces the latest text message or response part when DeepKeep returns modified content.
- `alert`: Allows the run to continue.

If DeepKeep returns an unsupported action, the capability fails closed.

## Configuration

- `api_key`: DeepKeep API key. If omitted, reads `DEEPKEEP_API_KEY`.
- `base_url`: DeepKeep base URL, without a trailing slash. If omitted, reads `DEEPKEEP_BASE_URL`.
- `pre_model`: DeepKeep firewall ID for pre-moderation.
- `post_model`: DeepKeep firewall ID for post-moderation.
- `title`: Optional title value sent to DeepKeep.
- `chat`: Optional chat value sent to DeepKeep.
- `timeout`: Request timeout in seconds. Defaults to `30.0`.
- `fail_closed`: Raise when DeepKeep cannot be reached. Defaults to `True`.

## Recommended Pydantic AI docs positioning

Position the public integration as DeepKeep AI Firewall in Pydantic AI's integrations or custom capabilities area:

```text
DeepKeep AI Firewall
Use DeepKeep AI Firewall as a custom Pydantic AI capability to enforce runtime guardrails before model requests and after model responses. Supports allow, block, redact, modify, and alert workflows for prompt injection, jailbreaks, sensitive data leakage, unsafe content, and other AI risks.
```
