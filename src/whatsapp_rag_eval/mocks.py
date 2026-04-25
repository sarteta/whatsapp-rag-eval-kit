"""Deterministic mock bot -- used for CI and for out-of-the-box demos so the
kit works without an LLM provider configured."""
from __future__ import annotations

import random
from typing import Callable

from .evaluators import BotResponse
from .loader import Case


ScriptedReply = dict[str, dict]

# A simple scripted bot that looks at keywords in the inbound and produces
# a canned answer + intent. Mirrors what a sloppy rule-first WhatsApp bot
# would do -- good enough to exercise the eval machinery.
DEFAULT_SCRIPT: ScriptedReply = {
    "horario|horarios|abren|cerrado|atencion": {
        "answer": "Atendemos de lunes a viernes de 9 a 18 hs. Los sabados de 9 a 13.",
        "intent": "schedule_query",
        "latency_ms": 1200,
        "cost_usd": 0.0012,
    },
    "turno|agendar|cita|reserva": {
        "answer": "Podes reservar tu turno desde nuestro sitio web o respondiendo este mensaje con tu DNI y la fecha que preferis.",
        "intent": "booking_intent",
        "latency_ms": 1400,
        "cost_usd": 0.0015,
    },
    "precio|cuesta|cuanto sale|costo": {
        "answer": "Los precios dependen del servicio. Respondenos con cual te interesa y te paso el valor vigente.",
        "intent": "price_query",
        "latency_ms": 1100,
        "cost_usd": 0.0011,
    },
    "cancelar|anular|perdi el turno": {
        "answer": "Podes cancelar escribiendo CANCELAR y tu DNI. Si es con menos de 24hs aplica cargo.",
        "intent": "cancel_intent",
        "latency_ms": 1050,
        "cost_usd": 0.0010,
    },
}


def keyword_matches(patterns: str, text: str) -> bool:
    text_lower = text.lower()
    return any(kw.strip() in text_lower for kw in patterns.split("|"))


def mock_bot(case: Case, script: ScriptedReply | None = None, jitter_ms: int = 0) -> BotResponse:
    """Deterministic bot response based on keyword match.

    `jitter_ms` adds bounded pseudo-random noise to latency. Deterministic per
    case id, so CI runs are reproducible.
    """
    script = script or DEFAULT_SCRIPT
    for patterns, reply in script.items():
        if keyword_matches(patterns, case.inbound):
            latency = reply["latency_ms"]
            if jitter_ms:
                # Seed by id for reproducibility -- same case -> same jitter
                r = random.Random(case.id)
                latency += r.randint(-jitter_ms, jitter_ms)
            return BotResponse(
                case_id=case.id,
                answer=reply["answer"],
                intent=reply["intent"],
                latency_ms=latency,
                cost_usd=reply["cost_usd"],
            )

    # Fallback -- triggers many failure modes intentionally so the report shows
    # actual problems.
    return BotResponse(
        case_id=case.id,
        answer="No se que decirte sobre eso, consultame otra cosa.",
        intent="unknown",
        latency_ms=2100,
        cost_usd=0.0018,
    )


BotFn = Callable[[Case], BotResponse]
