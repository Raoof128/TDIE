from __future__ import annotations

import inspect
import typing

import httpx
import pytest


def _patch_forward_ref_evaluation() -> None:
    """Align ForwardRef evaluation signature across Python versions for Pydantic."""

    if "recursive_guard" in typing.ForwardRef._evaluate.__code__.co_varnames:  # type: ignore[attr-defined]
        _orig_eval = typing.ForwardRef._evaluate  # type: ignore[attr-defined]
        orig_params = inspect.signature(_orig_eval).parameters

        def _patched_evaluate(
            self, globalns, localns, type_params=None, recursive_guard=None, **kwargs
        ):  # type: ignore[override]
            """Bridge signature differences without passing unsupported kwargs."""

            guard = (
                recursive_guard
                if recursive_guard is not None
                else kwargs.pop("recursive_guard", set())
            )

            # Only forward type_params when the wrapped implementation accepts it.
            if type_params is not None and "type_params" in orig_params:
                kwargs["type_params"] = type_params

            # Ensure we do not pass unexpected keywords to the underlying implementation.
            safe_kwargs = kwargs if "type_params" in orig_params else {}
            return _orig_eval(
                self,
                globalns,
                localns,
                recursive_guard=guard,
                **safe_kwargs,
            )

        typing.ForwardRef._evaluate = _patched_evaluate  # type: ignore[assignment]


_patch_forward_ref_evaluation()

from backend.main import app  # noqa: E402

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
async def client() -> typing.AsyncIterator[httpx.AsyncClient]:
    """Provide an HTTPX async client backed by the FastAPI ASGI app."""

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


def example_payload() -> dict:
    return {
        "schema": {
            "name": "synthetic_demo",
            "version": "1.0",
            "fields": [
                {"name": "id", "dtype": "int", "required": True},
                {
                    "name": "value",
                    "dtype": "float",
                    "required": True,
                    "min_value": 0,
                    "max_value": 50,
                },
                {"name": "group", "dtype": "str", "required": True},
                {"name": "label", "dtype": "int", "required": True},
                {"name": "timestamp", "dtype": "datetime", "required": True},
            ],
        },
        "records": [
            {"id": 1, "value": 10.5, "group": "A", "label": 1, "timestamp": "2024-01-01T00:00:00"},
            {"id": 2, "value": 9.7, "group": "B", "label": 0, "timestamp": "2024-01-02T00:00:00"},
            {"id": 3, "value": 11.2, "group": "A", "label": 1, "timestamp": "2024-01-03T00:00:00"},
        ],
        "source": "synthetic",
        "user": "tester",
        "transformation_steps": ["scaling"],
    }


async def test_health(client: httpx.AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.text == "ok"


async def test_validate_dataset(client: httpx.AsyncClient):
    response = await client.post("/validate_dataset", json=example_payload())
    assert response.status_code == 200
    data = response.json()
    assert "quality_score" in data
    assert "schema_violations" in data


async def test_fingerprint(client: httpx.AsyncClient):
    response = await client.post("/fingerprint", json=example_payload())
    assert response.status_code == 200
    data = response.json()
    assert "dataset_hash" in data
    assert "feature_hashes" in data


async def test_poison_and_bias(client: httpx.AsyncClient):
    payload = example_payload()
    poison_res = await client.post("/poison_detect", json=payload)
    bias_res = await client.post("/bias_check", json=payload)
    assert poison_res.status_code == 200
    assert bias_res.status_code == 200
    assert "poisoning_risk_score" in poison_res.json()
    assert "bias_integrity_score" in bias_res.json()


async def test_tdie_score_and_training_gate(client: httpx.AsyncClient):
    payload = example_payload()
    tdie_res = await client.post("/tdie_score", json=payload)
    assert tdie_res.status_code == 200
    tdie_score = tdie_res.json()["tdie_score"]

    train_res = await client.post(
        "/train_if_clean", json={"tdie_score": tdie_score, "guardrail_level": "PERMISSIVE"}
    )
    assert train_res.status_code == 200
    assert "training_decision" in train_res.json()
