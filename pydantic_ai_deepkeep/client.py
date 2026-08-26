from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


ACTION_PRIORITY = {"block": 4, "redact": 3, "modify": 3, "alert": 1}


class DeepKeepAPIError(Exception):
    """Raised when the DeepKeep API returns an error or a network request fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class DeepKeepDecision:
    action: str | None = None
    reason: str = "DeepKeep allowed this content."
    modified_content: str | None = None
    raw: dict[str, Any] | None = None
    unsupported_action: str | None = None

    @property
    def allowed(self) -> bool:
        return self.action != "block" and self.unsupported_action is None

    @property
    def should_replace(self) -> bool:
        return self.action in {"redact", "modify"} and self.modified_content is not None


class DeepKeepClient:
    """HTTP client for DeepKeep OpenAI-compatible moderation endpoints."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("DEEPKEEP_API_KEY")
        self.base_url = (base_url or os.environ.get("DEEPKEEP_BASE_URL") or "").rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("DeepKeep API key is required. Pass api_key or set DEEPKEEP_API_KEY.")
        if not self.base_url:
            raise ValueError("DeepKeep base URL is required. Pass base_url or set DEEPKEEP_BASE_URL.")

    async def async_pre_decision(
        self, *, model: str, input: str | list[str], title: str = "", chat: str = ""
    ) -> DeepKeepDecision:
        return decision_from_response(await self.async_pre_moderate(model=model, input=input, title=title, chat=chat))

    async def async_post_decision(
        self, *, model: str, output: str | list[str], title: str = "", chat: str = ""
    ) -> DeepKeepDecision:
        return decision_from_response(await self.async_post_moderate(model=model, output=output, title=title, chat=chat))

    async def async_pre_moderate(
        self,
        *,
        model: str,
        input: str | list[str],
        title: str = "",
        chat: str = "",
    ) -> dict[str, Any]:
        return await self._async_post(
            "/api/v3/openai/moderations/pre",
            {"model": model, "input": input, "title": title, "chat": chat},
        )

    async def async_post_moderate(
        self,
        *,
        model: str,
        output: str | list[str],
        title: str = "",
        chat: str = "",
    ) -> dict[str, Any]:
        return await self._async_post(
            "/api/v3/openai/moderations/post",
            {"model": model, "output": output, "title": title, "chat": chat},
        )

    async def _async_post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{path}",
                    headers={"X-API-Key": self.api_key, "Accept": "application/json"},
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise DeepKeepAPIError(f"DeepKeep network error: {exc}") from exc

        if response.status_code >= 400:
            raise DeepKeepAPIError(
                f"DeepKeep API error {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

        return response.json()


def decision_from_response(result: dict[str, Any]) -> DeepKeepDecision:
    selected: str | None = None
    unsupported: str | None = None
    reason = "DeepKeep allowed this content."
    modified_content: str | None = None

    for item in result.get("verbosity", []):
        if not isinstance(item, dict):
            continue
        details = item.get("details", {}) if isinstance(item.get("details"), dict) else {}
        action = details.get("guardrail_action")
        if action is None:
            continue
        if action not in ACTION_PRIORITY:
            unsupported = str(action)
            continue
        if selected is None or ACTION_PRIORITY[action] > ACTION_PRIORITY[selected]:
            selected = action
            reason = details.get("message") or details.get("reason") or item.get("message") or item.get("name") or reason

        for modified in details.get("modified", []) or []:
            if isinstance(modified, dict) and isinstance(modified.get("content"), str):
                modified_content = modified["content"]

    if modified_content is None:
        inputs = result.get("inputs", [])
        if inputs and isinstance(inputs[0], dict) and isinstance(inputs[0].get("content"), str):
            modified_content = inputs[0]["content"]

    return DeepKeepDecision(
        action=selected,
        reason=reason,
        modified_content=modified_content,
        raw=result,
        unsupported_action=unsupported,
    )
