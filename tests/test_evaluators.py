from whatsapp_rag_eval import evaluators
from whatsapp_rag_eval.evaluators import BotResponse
from whatsapp_rag_eval.loader import Case, Expect


def make_case(**expect_kwargs) -> Case:
    return Case(
        id="t",
        inbound="whatever",
        expect=Expect(**expect_kwargs),
    )


def make_resp(**kwargs) -> BotResponse:
    defaults = dict(case_id="t", answer="", intent=None, latency_ms=0, cost_usd=0.0)
    defaults.update(kwargs)
    return BotResponse(**defaults)


def test_intent_check_skipped_when_no_expected():
    assert evaluators.intent_check(make_case(), make_resp(intent="x")) is None


def test_intent_check_pass():
    r = evaluators.intent_check(make_case(intent="booking"), make_resp(intent="booking"))
    assert r is not None and r.passed


def test_intent_check_fail_on_mismatch():
    r = evaluators.intent_check(make_case(intent="booking"), make_resp(intent="price"))
    assert r is not None and not r.passed
    assert "booking" in r.detail and "price" in r.detail


def test_contains_case_insensitive():
    r = evaluators.contains_check(
        make_case(answer_contains=["LUNES"]),
        make_resp(answer="Abrimos los lunes."),
    )
    assert r is not None and r.passed


def test_contains_fails_reports_missing():
    r = evaluators.contains_check(
        make_case(answer_contains=["lunes", "viernes"]),
        make_resp(answer="Abrimos martes"),
    )
    assert r is not None and not r.passed
    assert "lunes" in r.detail and "viernes" in r.detail


def test_does_not_contain_passes():
    r = evaluators.does_not_contain_check(
        make_case(answer_does_not_contain=["no sé"]),
        make_resp(answer="Abrimos de 9 a 18"),
    )
    assert r is not None and r.passed


def test_does_not_contain_fails_reports_hit():
    r = evaluators.does_not_contain_check(
        make_case(answer_does_not_contain=["no sé"]),
        make_resp(answer="La verdad no sé esa info"),
    )
    assert r is not None and not r.passed
    assert "no sé" in r.detail


def test_regex_check_skipped_when_empty():
    assert evaluators.regex_check(make_case(), make_resp(answer="anything")) is None


def test_regex_check_pass_single_pattern():
    r = evaluators.regex_check(
        make_case(answer_matches_regex=[r"\b\d{4}\b"]),
        make_resp(answer="Tu codigo de reserva es 4821, gracias."),
    )
    assert r is not None and r.passed


def test_regex_check_fail_reports_unmatched():
    r = evaluators.regex_check(
        make_case(answer_matches_regex=[r"\b\d{4}\b", r"gracias"]),
        make_resp(answer="Reserva confirmada."),
    )
    assert r is not None and not r.passed
    assert "gracias" in r.detail


def test_regex_check_invalid_pattern_fails_clearly():
    r = evaluators.regex_check(
        make_case(answer_matches_regex=["[unclosed"]),
        make_resp(answer="anything"),
    )
    assert r is not None and not r.passed
    assert "invalid regex" in r.detail


def test_latency_pass_and_fail():
    assert evaluators.latency_check(make_case(max_latency_ms=1000), make_resp(latency_ms=900)).passed
    assert not evaluators.latency_check(make_case(max_latency_ms=1000), make_resp(latency_ms=1200)).passed


def test_cost_pass_and_fail():
    assert evaluators.cost_check(make_case(max_cost_usd=0.01), make_resp(cost_usd=0.005)).passed
    assert not evaluators.cost_check(make_case(max_cost_usd=0.01), make_resp(cost_usd=0.02)).passed


def test_run_all_skips_none_checks():
    # Empty expect -> all evaluators return None -> run_all returns []
    assert evaluators.run_all(make_case(), make_resp()) == []
