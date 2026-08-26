from pydantic_ai_deepkeep import decision_from_response


def test_decision_prefers_block():
    result = {
        "verbosity": [
            {"details": {"guardrail_action": "alert"}},
            {"details": {"guardrail_action": "redact"}},
            {"details": {"guardrail_action": "block", "message": "blocked"}},
        ]
    }

    decision = decision_from_response(result)

    assert decision.action == "block"
    assert decision.reason == "blocked"
    assert not decision.allowed


def test_decision_uses_latest_modified_item():
    result = {
        "verbosity": [
            {"details": {"guardrail_action": "redact", "modified": [{"content": "first"}]}},
            {"details": {"guardrail_action": "redact", "modified": [{"content": "second"}]}},
        ]
    }

    decision = decision_from_response(result)

    assert decision.action == "redact"
    assert decision.modified_content == "second"
    assert decision.should_replace


def test_decision_records_unsupported_action():
    result = {"verbosity": [{"details": {"guardrail_action": "quarantine"}}]}

    decision = decision_from_response(result)

    assert decision.unsupported_action == "quarantine"
    assert not decision.allowed
