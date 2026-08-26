"""
DeepKeep AI Firewall Guardrails for Pydantic AI
===============================================

This example shows how to use DeepKeep AI Firewall as a Pydantic AI custom
capability. DeepKeep runs before user input reaches the model and after model
output is generated.

Set credentials before running:

    export DEEPKEEP_API_KEY="dk_..."
    export DEEPKEEP_BASE_URL="https://api.example.deepkeep.ai"
"""

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


if __name__ == "__main__":
    result = agent.run_sync("Explain how to store API keys securely.")
    print(result.output)
