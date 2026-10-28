"""Unit tests for the isolated Python code runner."""
import pytest
from app.services.code_runner import run_python


def test_code_runner_correct_solution():
    test_cases = [
        {"input": "hello world", "expected": "world hello"},
        {"input": "Python is fast", "expected": "fast is Python"},
        {"input": "single", "expected": "single"}
    ]
    code = """def reverse_words(s):
    return " ".join(s.split()[::-1])
"""
    result = run_python(code, test_cases, target_func_name="reverse_words")
    assert result["passed"] == 3
    assert result["total"] == 3
    assert result["score"] == 20.0
    assert result["error"] is None


def test_code_runner_incorrect_solution():
    test_cases = [
        {"input": "hello world", "expected": "world hello"},
        {"input": "single", "expected": "single"}
    ]
    code = """def reverse_words(s):
    return s
"""
    result = run_python(code, test_cases, target_func_name="reverse_words")
    assert result["passed"] == 1
    assert result["total"] == 2
    assert result["score"] == 10.0


def test_code_runner_syntax_error():
    test_cases = [{"input": "test", "expected": "test"}]
    code = "def reverse_words(s) return s"  # missing colon
    result = run_python(code, test_cases, target_func_name="reverse_words")
    assert result["passed"] == 0
    assert "Syntax" in result["error"]


def test_code_runner_timeout():
    test_cases = [{"input": "test", "expected": "test"}]
    code = """def reverse_words(s):
    while True:
        pass
"""
    result = run_python(code, test_cases, target_func_name="reverse_words", time_limit=1.0)
    assert result["passed"] == 0
    assert "timed out" in result["error"].lower()


def test_code_runner_security_sandbox():
    test_cases = [{"input": "test", "expected": "test"}]
    code = """def reverse_words(s):
    import os
    return "blocked"
"""
    result = run_python(code, test_cases, target_func_name="reverse_words")
    assert result["passed"] == 0
    assert len(result["details"]) > 0
    assert "restricted" in result["details"][0]["error"].lower()
