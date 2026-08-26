from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from pydantic_ai import ModelRequestContext, RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ModelResponse

from .client import DeepKeepAPIError, DeepKeepClient, DeepKeepDecision


class DeepKeepBlockedError(RuntimeError):
    """Raised when DeepKeep blocks content or returns an unsupported action."""

    def __init__(self, decision: DeepKeepDecision, *, phase: str) -> None:
        if decision.unsupported_action:
            message = f"DeepKeep returned unsupported guardrail action: {decision.unsupported_action}"
        else:
            message = decision.reason
        super().__init__(message)
        self.decision = decision
        self.phase = phase


@dataclass
class DeepKeepGuardrail(AbstractCapability[Any]):
    """Pydantic AI capability that runs DeepKeep before and after model requests."""

    pre_model: str | None = None
    post_model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    title: str = ""
    chat: str = ""
    timeout: float = 30.0
    fail_closed: bool = True
    id: str | None = "deepkeep-ai-firewall"
    description: str | None = "DeepKeep AI Firewall input and output guardrails."
    defer_loading: bool = False

    def __post_init__(self) -> None:
        if not self.pre_model and not self.post_model:
            raise ValueError("At least one of pre_model or post_model is required.")
        self.client = DeepKeepClient(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    @classmethod
    def get_serialization_name(cls) -> str:
        return "DeepKeepGuardrail"

    async def before_model_request(
        self, ctx: RunContext[Any], request_context: ModelRequestContext
    ) -> ModelRequestContext:
        if not self.pre_model:
            return request_context

        text = _text_from_messages(request_context.messages)
        if not text:
            return request_context

        try:
            decision = await self.client.async_pre_decision(
                model=self.pre_model,
                input=text,
                title=self.title,
                chat=self.chat,
            )
        except DeepKeepAPIError:
            if self.fail_closed:
                raise
            return request_context

        _raise_if_blocked(decision, phase="pre")
        if decision.should_replace:
            return replace(request_context, messages=_replace_last_text(request_context.messages, decision.modified_content or text))
        return request_context

    async def after_model_request(
        self,
        ctx: RunContext[Any],
        *,
        request_context: ModelRequestContext,
        response: ModelResponse,
    ) -> ModelResponse:
        if not self.post_model:
            return response

        text = _text_from_messages([response])
        if not text:
            return response

        try:
            decision = await self.client.async_post_decision(
                model=self.post_model,
                output=text,
                title=self.title,
                chat=self.chat,
            )
        except DeepKeepAPIError:
            if self.fail_closed:
                raise
            return response

        _raise_if_blocked(decision, phase="post")
        if decision.should_replace:
            return _replace_response_text(response, decision.modified_content or text)
        return response


def _raise_if_blocked(decision: DeepKeepDecision, *, phase: str) -> None:
    if decision.unsupported_action or decision.action == "block":
        raise DeepKeepBlockedError(decision, phase=phase)


def _text_from_messages(messages: list[Any]) -> str:
    values: list[str] = []
    for message in messages:
        for part in getattr(message, "parts", []) or []:
            content = getattr(part, "content", None)
            if isinstance(content, str):
                values.append(content)
            elif isinstance(content, list):
                values.extend(str(item) for item in content if isinstance(item, str))
    return "\n".join(values)


def _replace_last_text(messages: list[Any], content: str) -> list[Any]:
    updated = list(messages)
    for message_index in range(len(updated) - 1, -1, -1):
        parts = list(getattr(updated[message_index], "parts", []) or [])
        for part_index in range(len(parts) - 1, -1, -1):
            if isinstance(getattr(parts[part_index], "content", None), str):
                parts[part_index] = replace(parts[part_index], content=content)
                updated[message_index] = replace(updated[message_index], parts=parts)
                return updated
    return updated


def _replace_response_text(response: ModelResponse, content: str) -> ModelResponse:
    parts = list(getattr(response, "parts", []) or [])
    for index in range(len(parts) - 1, -1, -1):
        if isinstance(getattr(parts[index], "content", None), str):
            parts[index] = replace(parts[index], content=content)
            return replace(response, parts=parts)
    return response
