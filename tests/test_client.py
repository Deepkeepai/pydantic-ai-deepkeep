import pytest
import respx
from httpx import Response

from pydantic_ai_deepkeep import DeepKeepAPIError, DeepKeepClient


@pytest.mark.asyncio
@respx.mock
async def test_pre_moderate_posts_to_pre_endpoint():
    route = respx.post("https://deepkeep.example/api/v3/openai/moderations/pre").mock(
        return_value=Response(200, json={"flagged": False, "verbosity": []})
    )

    client = DeepKeepClient(api_key="dk-test", base_url="https://deepkeep.example")
    result = await client.async_pre_moderate(model="fw-input", input="hello")

    assert result["flagged"] is False
    assert route.calls.last.request.headers["X-API-Key"] == "dk-test"
    assert route.calls.last.request.content == b'{"model":"fw-input","input":"hello","title":"","chat":""}'


@pytest.mark.asyncio
@respx.mock
async def test_post_moderate_posts_to_post_endpoint():
    route = respx.post("https://deepkeep.example/api/v3/openai/moderations/post").mock(
        return_value=Response(200, json={"flagged": False, "verbosity": []})
    )

    client = DeepKeepClient(api_key="dk-test", base_url="https://deepkeep.example/")
    result = await client.async_post_moderate(model="fw-output", output="hello")

    assert result["flagged"] is False
    assert route.calls.last.request.content == b'{"model":"fw-output","output":"hello","title":"","chat":""}'


@pytest.mark.asyncio
@respx.mock
async def test_api_error_keeps_status_code():
    respx.post("https://deepkeep.example/api/v3/openai/moderations/pre").mock(
        return_value=Response(404, json={"detail": "No firewall with the provided identifier."})
    )

    client = DeepKeepClient(api_key="dk-test", base_url="https://deepkeep.example")
    with pytest.raises(DeepKeepAPIError) as exc_info:
        await client.async_pre_moderate(model="missing", input="hello")

    assert exc_info.value.status_code == 404
