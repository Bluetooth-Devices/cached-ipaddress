"""
Tests for the construction-caching contract of cached_ip_addresses.

These tests lock the library's headline guarantee: building an address from
the same input returns the *same* cached object, and unparsable input is
turned into ``None`` (also cached) rather than raising. The existing
``test_ipaddress.py`` exercises per-address property caching; this module
covers the wrapper-level caching semantics that were previously untested.
"""

from ipaddress import IPv4Address, IPv6Address

import pytest

from cached_ipaddress import ipaddress
from cached_ipaddress.ipaddress import (
    CachedIPv4Address,
    CachedIPv6Address,
    cached_ip_addresses,
)


def test_same_input_returns_same_object():
    """Repeated calls with the same input return the identical cached object."""
    first = cached_ip_addresses("1.2.3.4")
    second = cached_ip_addresses("1.2.3.4")
    assert first is second


def test_distinct_inputs_return_distinct_objects():
    """Different inputs produce different objects."""
    assert cached_ip_addresses("1.2.3.4") is not cached_ip_addresses("1.2.3.5")


def test_cache_keyed_by_raw_input_not_resolved_address():
    """Equal-but-different-typed inputs are distinct keys, so distinct objects."""
    from_str = cached_ip_addresses("127.0.0.1")
    from_bytes = cached_ip_addresses(b"\x7f\x00\x00\x01")
    assert from_str is not from_bytes
    assert from_str == from_bytes


@pytest.mark.parametrize(
    "invalid",
    ["", "foo", "1.2.3.04", "256.0.0.0", "1.2.3.4.5", "::g", "12345::"],
)
def test_invalid_input_returns_none(invalid):
    """Unparsable addresses resolve to None instead of raising."""
    assert cached_ip_addresses(invalid) is None


def test_none_result_is_cached():
    """The None result for invalid input is returned consistently on retry."""
    assert cached_ip_addresses("not-an-ip") is None
    assert cached_ip_addresses("not-an-ip") is None


@pytest.mark.parametrize(
    ("value", "expected_type"),
    [
        ("1.2.3.4", CachedIPv4Address),
        (b"\x7f\x00\x00\x01", CachedIPv4Address),
        (0, CachedIPv4Address),
        (2**32 - 1, CachedIPv4Address),
        ("::1", CachedIPv6Address),
        ("2606:2800:220:1:248:1893:25c8:1946", CachedIPv6Address),
    ],
)
def test_dispatches_to_correct_cached_type(value, expected_type):
    """str/bytes/int inputs dispatch to the right cached address subclass."""
    result = cached_ip_addresses(value)
    assert type(result) is expected_type


def test_returns_subclass_of_stdlib_types():
    """Cached addresses remain instances of the stdlib types they extend."""
    assert isinstance(cached_ip_addresses("1.2.3.4"), IPv4Address)
    assert isinstance(cached_ip_addresses("::1"), IPv6Address)


@pytest.mark.parametrize("value", ["192.168.1.1", "::1", "fe80::1", "8.8.8.8"])
def test_equality_hash_and_int_match_stdlib(value):
    """A cached address compares, hashes, and int-converts like the stdlib one."""
    cached = cached_ip_addresses(value)
    assert cached is not None
    plain = (
        IPv4Address(value) if isinstance(cached, IPv4Address) else IPv6Address(value)
    )
    assert cached == plain
    assert hash(cached) == hash(plain)
    assert int(cached) == int(plain)


def test_public_wrapper_is_module_level_callable():
    """The exported name and the module attribute reference the same wrapper."""
    assert ipaddress.cached_ip_addresses is cached_ip_addresses


def test_cache_info_reports_hits_and_misses():
    """``cache_info()`` reflects miss-then-hit behaviour for the same input."""
    cached_ip_addresses.cache_clear()
    before = cached_ip_addresses.cache_info()
    assert before.hits == 0
    assert before.misses == 0

    cached_ip_addresses("10.0.0.1")
    cached_ip_addresses("10.0.0.1")
    cached_ip_addresses("10.0.0.1")

    after = cached_ip_addresses.cache_info()
    assert after.misses == 1
    assert after.hits == 2
    assert after.currsize == 1


def test_cache_clear_drops_cached_objects():
    """``cache_clear()`` evicts existing entries so a new object is produced."""
    cached_ip_addresses.cache_clear()
    first = cached_ip_addresses("172.16.0.1")
    assert cached_ip_addresses.cache_info().currsize == 1

    cached_ip_addresses.cache_clear()
    assert cached_ip_addresses.cache_info().currsize == 0

    second = cached_ip_addresses("172.16.0.1")
    assert first is not second
    assert first == second


def test_cache_maxsize_is_535():
    """The advertised LRU bound stays at 535 entries."""
    assert cached_ip_addresses.cache_info().maxsize == 535


def test_lru_evicts_oldest_when_over_capacity():
    """Filling the cache past ``maxsize`` evicts the oldest entry."""
    cached_ip_addresses.cache_clear()
    maxsize = cached_ip_addresses.cache_info().maxsize
    assert maxsize is not None

    oldest = cached_ip_addresses("10.0.0.0")
    for i in range(1, maxsize):
        cached_ip_addresses(f"10.0.{i // 256}.{i % 256}")

    info = cached_ip_addresses.cache_info()
    assert info.currsize == maxsize

    # One more unique input pushes the oldest out.
    cached_ip_addresses(f"10.0.{maxsize // 256}.{maxsize % 256}")
    assert cached_ip_addresses.cache_info().currsize == maxsize

    # Re-requesting the original is now a miss → fresh object.
    reborn = cached_ip_addresses("10.0.0.0")
    assert reborn is not oldest
    assert reborn == oldest


def test_none_results_consume_a_cache_slot():
    """Unparsable inputs are cached too, so they count toward ``currsize``."""
    cached_ip_addresses.cache_clear()
    assert cached_ip_addresses("not-an-ip") is None
    assert cached_ip_addresses("not-an-ip") is None

    info = cached_ip_addresses.cache_info()
    assert info.misses == 1
    assert info.hits == 1
    assert info.currsize == 1
