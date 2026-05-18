"""
Tests unitarios para app/core/metrics.py

Cubre: _parse_labels, _parse_metric_line (parseo sin regex).
No requiere red, Docker ni PostgreSQL.
"""

import pytest

from app.core.metrics import (
    _parse_labels, _parse_metric_line,
    _status_badge_class, _latency_evaluation,
    _collect_latency_metrics, _consolidate_latency_data,
    _build_latency_table_rows,
)


class TestParseLabels:

    def test_single_label(self):
        result = _parse_labels('handler="/health"')
        assert result == {"handler": "/health"}

    def test_multiple_labels(self):
        result = _parse_labels('method="GET",handler="/api/matches",status="200"')
        assert result == {
            "method": "GET",
            "handler": "/api/matches",
            "status": "200",
        }

    def test_empty_string(self):
        result = _parse_labels("")
        assert result == {}

    def test_label_with_spaces(self):
        result = _parse_labels(' method="POST" , handler="/api/auth/login" ')
        assert result == {"method": "POST", "handler": "/api/auth/login"}

    def test_label_with_empty_value(self):
        result = _parse_labels('handler=""')
        assert result == {"handler": ""}

    def test_malformed_no_equals(self):
        result = _parse_labels("noequalshere")
        assert result == {}


class TestParseMetricLine:

    def test_sum_metric(self):
        line = 'http_request_duration_seconds_sum{method="GET",handler="/health",status="200"} 0.123'
        result = _parse_metric_line(line)
        assert result is not None
        metric, labels, value = result
        assert metric == "http_request_duration_seconds_sum"
        assert labels["method"] == "GET"
        assert labels["handler"] == "/health"
        assert labels["status"] == "200"
        assert value == pytest.approx(0.123)

    def test_count_metric(self):
        line = 'http_request_duration_seconds_count{method="POST",handler="/api/auth/register",status="201"} 5.0'
        result = _parse_metric_line(line)
        assert result is not None
        metric, labels, value = result
        assert metric == "http_request_duration_seconds_count"
        assert labels["method"] == "POST"
        assert labels["handler"] == "/api/auth/register"
        assert labels["status"] == "201"
        assert value == 5.0

    def test_ignores_unrelated_metric(self):
        line = 'python_gc_objects_collected_total{generation="0"} 1234.0'
        result = _parse_metric_line(line)
        assert result is None

    def test_ignores_comment_lines(self):
        line = "# HELP http_request_duration_seconds_sum Total duration"
        result = _parse_metric_line(line)
        assert result is None

    def test_ignores_type_lines(self):
        line = "# TYPE http_request_duration_seconds_sum summary"
        result = _parse_metric_line(line)
        assert result is None

    def test_ignores_line_without_braces(self):
        line = "http_request_duration_seconds_sum 0.5"
        result = _parse_metric_line(line)
        assert result is None

    def test_ignores_line_with_no_value(self):
        line = 'http_request_duration_seconds_sum{method="GET"}'
        result = _parse_metric_line(line)
        assert result is None

    def test_ignores_line_with_invalid_value(self):
        line = 'http_request_duration_seconds_sum{method="GET"} notanumber'
        result = _parse_metric_line(line)
        assert result is None

    def test_large_value(self):
        line = 'http_request_duration_seconds_sum{method="GET",handler="/api/matches",status="200"} 12345.6789'
        result = _parse_metric_line(line)
        assert result is not None
        _, _, value = result
        assert value == pytest.approx(12345.6789)

    def test_no_backtracking_on_adversarial_input(self):
        adversarial = 'http_request_duration_seconds_sum{' + 'a="b",' * 1000 + '} 1.0'
        result = _parse_metric_line(adversarial)
        assert result is not None
        _, labels, value = result
        assert labels.get("a") == "b"
        assert value == 1.0


class TestStatusBadgeClass:

    def test_status_2xx(self):
        assert _status_badge_class("200") == "bg-success"

    def test_status_5xx(self):
        assert _status_badge_class("500") == "bg-danger"

    def test_status_4xx(self):
        assert _status_badge_class("404") == "bg-warning text-dark"


class TestLatencyEvaluation:

    def test_excelente(self):
        assert "Excelente" in _latency_evaluation(50)

    def test_bueno(self):
        assert "Bueno" in _latency_evaluation(150)

    def test_aceptable(self):
        assert "Aceptable" in _latency_evaluation(300)

    def test_lento(self):
        assert "Lento" in _latency_evaluation(600)


SAMPLE_METRICS_TEXT = "\n".join([
    "# HELP http_request_duration_seconds_sum Total duration",
    "# TYPE http_request_duration_seconds_sum summary",
    'http_request_duration_seconds_sum{method="GET",handler="/health",status="200"} 0.5',
    'http_request_duration_seconds_count{method="GET",handler="/health",status="200"} 10.0',
    'http_request_duration_seconds_sum{method="POST",handler="/api/auth/login",status="201"} 1.2',
    'http_request_duration_seconds_count{method="POST",handler="/api/auth/login",status="201"} 4.0',
    'python_gc_objects_collected_total{generation="0"} 1234.0',
])


class TestCollectLatencyMetrics:

    def test_collects_sum_and_count(self):
        sumas, conteos = _collect_latency_metrics(SAMPLE_METRICS_TEXT)
        key = ("GET", "/health", "200")
        assert key in sumas
        assert sumas[key] == pytest.approx(0.5)
        assert conteos[key] == 10

    def test_ignores_unrelated_metrics(self):
        sumas, conteos = _collect_latency_metrics(SAMPLE_METRICS_TEXT)
        assert len(sumas) == 2
        assert len(conteos) == 2

    def test_empty_input(self):
        sumas, conteos = _collect_latency_metrics("")
        assert sumas == {}
        assert conteos == {}


class TestConsolidateLatencyData:

    def test_calculates_average_ms(self):
        sumas = {("GET", "/health", "200"): 0.5}
        conteos = {("GET", "/health", "200"): 10}
        datos = _consolidate_latency_data(sumas, conteos)
        assert len(datos) == 1
        method, handler, status, total, promedio = datos[0]
        assert total == 10
        assert promedio == pytest.approx(50.0)

    def test_sorts_by_latency_descending(self):
        sumas = {
            ("GET", "/fast", "200"): 0.1,
            ("GET", "/slow", "200"): 5.0,
        }
        conteos = {
            ("GET", "/fast", "200"): 10,
            ("GET", "/slow", "200"): 10,
        }
        datos = _consolidate_latency_data(sumas, conteos)
        assert datos[0][1] == "/slow"
        assert datos[1][1] == "/fast"

    def test_zero_count_returns_zero_average(self):
        sumas = {("GET", "/x", "200"): 1.0}
        conteos = {("GET", "/x", "200"): 0}
        datos = _consolidate_latency_data(sumas, conteos)
        assert datos[0][4] == 0

    def test_empty_input(self):
        assert _consolidate_latency_data({}, {}) == []


class TestBuildLatencyTableRows:

    def test_empty_returns_placeholder(self):
        result = _build_latency_table_rows([])
        assert "No hay peticiones registradas" in result

    def test_generates_html_rows(self):
        datos = [("GET", "/health", "200", 10, 50.0)]
        result = _build_latency_table_rows(datos)
        assert "GET" in result
        assert "/health" in result
        assert "200" in result
        assert "50.0 ms" in result
        assert "bg-success" in result

    def test_slow_endpoint_has_alert(self):
        datos = [("POST", "/slow", "500", 5, 600.0)]
        result = _build_latency_table_rows(datos)
        assert "table-danger" in result
        assert "bg-danger" in result
