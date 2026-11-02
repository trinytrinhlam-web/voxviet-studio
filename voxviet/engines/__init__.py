"""Đăng ký engine. Quy ước: mọi engine trả float32 mono ở ``audio.SR`` (48 kHz)."""

from __future__ import annotations

import os

from .base import EngineUnavailable, SynthRequest, TTSEngine
from .chatterbox_engine import ChatterboxEngine
from .google_engines import GeminiEngine, GTTSEngine
from .mock_engine import MockEngine
from .vieneu_engine import VieNeuEngine

__all__ = ["EngineUnavailable", "SynthRequest", "TTSEngine", "registry", "get"]

_REGISTRY: dict[str, TTSEngine] | None = None


def registry() -> dict[str, TTSEngine]:
    global _REGISTRY
    if _REGISTRY is None:
        engines: list[TTSEngine] = [VieNeuEngine(), ChatterboxEngine(), GeminiEngine(), GTTSEngine()]
        if os.environ.get("VOXVIET_DEMO") == "1":
            engines.insert(0, MockEngine())
        _REGISTRY = {e.id: e for e in engines}
    return _REGISTRY


def get(engine_id: str) -> TTSEngine:
    reg = registry()
    if engine_id not in reg:
        raise EngineUnavailable(f"Không có engine '{engine_id}'.")
    return reg[engine_id]


def offline_engines(language: str) -> list[TTSEngine]:
    return [e for e in registry().values() if not e.online and language in e.languages]
