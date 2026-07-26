"""Assert the test run exercises the build variant CI selected."""

import os

import pytest

from cached_ipaddress import ipaddress

EXPECTED = os.environ.get("CACHED_IPADDRESS_EXPECT_EXTENSION")


@pytest.mark.skipif(not EXPECTED, reason="build variant not pinned by the environment")
def test_build_variant_matches_ci_matrix() -> None:
    """The imported module must match the matrix leg that installed it."""
    # ``pyproject.toml`` puts ``src`` at the front of ``sys.path`` via pytest's
    # ``pythonpath``. If the compiled extension ever lands anywhere other than
    # in-place next to ``ipaddress.py``, that entry shadows it and the
    # ``use_cython`` legs test the pure-Python module while staying green.
    compiled = not ipaddress.__file__.endswith(".py")
    assert compiled is (EXPECTED == "use_cython"), (
        f"expected {EXPECTED!r} build, imported {ipaddress.__file__}"
    )
