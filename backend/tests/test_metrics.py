"""
Tests unitarios para app/core/metrics.py

Cubre: _parse_labels, _parse_metric_line (parseo sin regex).
No requiere red, Docker ni PostgreSQL.
"""

import pytest

from app.core.metrics import _parse_labels, _parse_metric_line


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
