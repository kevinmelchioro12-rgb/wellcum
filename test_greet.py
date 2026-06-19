"""Tests for the greet utility."""

from greet import greet


def test_greet_with_name():
    assert greet("Kevin") == "Hello, Kevin!"


def test_greet_without_name():
    assert greet() == "Hello there!"


def test_greet_strips_whitespace():
    assert greet("  Kevin  ") == "Hello, Kevin!"


def test_greet_blank_falls_back():
    assert greet("   ") == "Hello there!"
