"""
Tests for the ``REQUIRE_CYTHON`` contract in ``build_ext.py``.

The C extension is *optional*: a build on a machine with no working compiler
must still succeed and fall back to pure Python. ``REQUIRE_CYTHON`` opts out of
that leniency — CI sets it for the cibuildwheel legs precisely so that a
platform-tagged wheel can never be published without the compiled module in it.

These tests pin both halves of that contract at the compile/link step, which is
the half that ``build()``'s own ``REQUIRE_CYTHON`` guard does not cover.
"""

import pytest
from setuptools.command.build_ext import build_ext

import build_ext as build_ext_module


def _explode(self):
    raise RuntimeError("compiler exploded")


@pytest.fixture
def failing_build_ext(monkeypatch):
    """Return a BuildExt whose inherited compile step always fails."""
    # Patching the parent makes BuildExt's own super() call raise, so no real
    # Distribution or toolchain is needed.
    monkeypatch.setattr(build_ext, "build_extensions", _explode)
    return build_ext_module.BuildExt.__new__(build_ext_module.BuildExt)


def test_compile_failure_is_swallowed_by_default(monkeypatch, failing_build_ext):
    """Without REQUIRE_CYTHON the extension is optional, so failure is ignored."""
    monkeypatch.delenv("REQUIRE_CYTHON", raising=False)
    assert failing_build_ext.build_extensions() is None


def test_compile_failure_is_fatal_when_cython_required(monkeypatch, failing_build_ext):
    """With REQUIRE_CYTHON a failed compile must abort the build, not fall back."""
    monkeypatch.setenv("REQUIRE_CYTHON", "1")
    with pytest.raises(RuntimeError, match="compiler exploded"):
        failing_build_ext.build_extensions()


def test_skip_cython_short_circuits(monkeypatch):
    """SKIP_CYTHON wins outright: no ext_modules, no compile attempt."""
    monkeypatch.setenv("SKIP_CYTHON", "1")
    monkeypatch.setenv("REQUIRE_CYTHON", "1")
    kwargs = {"packages": ["cached_ipaddress"]}
    build_ext_module.build(kwargs)
    assert kwargs == {"packages": ["cached_ipaddress"]}
