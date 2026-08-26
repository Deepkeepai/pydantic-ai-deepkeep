import pytest

pytest.importorskip("pydantic_ai")

from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models import ModelRequestContext, ModelRequestParameters
from pydantic_ai.models.test import TestModel

from pydantic_ai_deepkeep import DeepKeepBlockedError, DeepKeepDecision, DeepKeepGuardrail


class FakeClient:
    def __init__(self, decision):
        self.decision = decision
        self.kwargs = None

    async def async_pre_decision(self, **kwargs):
        self.kwargs = kwargs
        return self.decision

    async def async_post_decision(self, **kwargs):
        self.kwargs = kwargs
        return self.decision


def guardrail_with(decision, *, pre_model="input-firewall", post_model="output-firewall"):
    guardrail = DeepKeepGuardrail(
        api_key="dk-test",
        base_url="https://deepkeep.example",
        pre_model=pre_model,
        post_model=post_model,
    )
    guardrail.client = FakeClient(decision)
    return guardrail


def request_context(content="hello"):
    return ModelRequestContext(
        model=TestModel(),
        messages=[ModelRequest(parts=[UserPromptPart(content)])],
        model_settings=None,
        model_request_parameters=ModelRequestParameters(),
    )


@pytest.mark.asyncio
async def test_before_model_request_replaces_redacted_input():
    guardrail = guardrail_with(DeepKeepDecision(action="redact", modified_content="safe"))

    updated = await guardrail.before_model_request(None, request_context("secret"))

    assert updated.messages[-1].parts[-1].content == "safe"
    assert guardrail.client.kwargs["model"] == "input-firewall"
    assert guardrail.client.kwargs["input"] == "secret"


@pytest.mark.asyncio
async def test_before_model_request_blocks_input():
    guardrail = guardrail_with(DeepKeepDecision(action="block", reason="blocked"))

    with pytest.raises(DeepKeepBlockedError) as exc_info:
        await guardrail.before_model_request(None, request_context("bad"))

    assert exc_info.value.phase == "pre"
    assert "blocked" in str(exc_info.value)


@pytest.mark.asyncio
async def test_after_model_request_replaces_redacted_output():
    guardrail = guardrail_with(DeepKeepDecision(action="modify", modified_content="safe output"))
    response = ModelResponse(parts=[TextPart("unsafe output")])

    updated = await guardrail.after_model_request(None, request_context=request_context(), response=response)

    assert updated.parts[-1].content == "safe output"
    assert guardrail.client.kwargs["model"] == "output-firewall"
    assert guardrail.client.kwargs["output"] == "unsafe output"
