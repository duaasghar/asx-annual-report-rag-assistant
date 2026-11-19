"""Smoke tests for the FastAPI backend. No Gemini calls are made:
the chain and retriever are replaced with stubs where /ask is exercised."""

import os

os.environ.setdefault("GOOGLE_API_KEY", "test-key-not-used")

import pytest
from fastapi.testclient import TestClient

import api

client = TestClient(api.app)


class StubChain:
    def invoke(self, question: str) -> str:
        return "Stub answer (Page 12)"


class StubRetriever:
    def invoke(self, question: str):
        from langchain_core.documents import Document

        return [Document(page_content="Operating revenue $1,107.2m", metadata={"page_number": 12})]


class FailingChain:
    def invoke(self, question: str):
        raise RuntimeError("503 UNAVAILABLE")


def test_health_reports_index_loaded():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["chunks"] > 0


@pytest.mark.parametrize("path", ["/", "/health"])
def test_head_supported_for_uptime_monitors(path):
    assert client.head(path).status_code == 200


@pytest.mark.parametrize("question", ["", "x" * 501])
def test_ask_rejects_invalid_questions(question):
    assert client.post("/ask", json={"question": question}).status_code == 422


def test_cors_blocks_unknown_origin():
    res = client.options(
        "/ask",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in res.headers


def test_ask_returns_typed_answer(monkeypatch):
    monkeypatch.setattr(api, "chain", StubChain())
    monkeypatch.setattr(api, "retriever", StubRetriever())
    res = client.post("/ask", json={"question": "  What was revenue?  "})
    assert res.status_code == 200
    assert res.json() == {
        "question": "What was revenue?",
        "answer": "Stub answer (Page 12)",
        "sources": [{"page": 12, "excerpt": "Operating revenue $1,107.2m"}],
    }


def test_ask_returns_503_when_model_unavailable(monkeypatch):
    monkeypatch.setattr(api, "chain", FailingChain())
    res = client.post("/ask", json={"question": "What was revenue?"})
    assert res.status_code == 503
    assert "busy" in res.json()["detail"]
