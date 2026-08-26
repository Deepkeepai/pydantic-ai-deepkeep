from .client import DeepKeepAPIError, DeepKeepClient, DeepKeepDecision, decision_from_response

__all__ = [
    "DeepKeepAPIError",
    "DeepKeepBlockedError",
    "DeepKeepClient",
    "DeepKeepDecision",
    "DeepKeepGuardrail",
    "decision_from_response",
]


def __getattr__(name: str):
    if name in {"DeepKeepBlockedError", "DeepKeepGuardrail"}:
        from .capability import DeepKeepBlockedError, DeepKeepGuardrail

        return {"DeepKeepBlockedError": DeepKeepBlockedError, "DeepKeepGuardrail": DeepKeepGuardrail}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
