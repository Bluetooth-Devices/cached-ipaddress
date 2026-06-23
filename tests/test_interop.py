"""
Stdlib interop contract for CachedIPv4Address / CachedIPv6Address.

Pins the behaviours downstream callers rely on when mixing
``cached_ip_addresses`` output with raw ``ipaddress`` stdlib objects:
symmetric equality, hash compatibility (dedup in sets and dict lookup),
sortability in a mixed list, network containment, and ``isinstance``
to the stdlib base classes. None of this is exercised by the existing
property/caching suites — a future change to ``__hash__``, ``__eq__``,
or the class hierarchy could silently break consumers.
"""

from __future__ import annotations

import ipaddress as stdlib_ipaddress
from ipaddress import (
    IPv4Address,
    IPv4Network,
    IPv6Address,
    IPv6Network,
)

import pytest

from cached_ipaddress import ipaddress as ci
from cached_ipaddress.ipaddress import CachedIPv4Address, CachedIPv6Address


@pytest.fixture(autouse=True)
def _clear_factory_cache() -> None:
    """Each test gets a fresh LRU so instance identity is predictable."""
    ci._cached_ip_addresses.cache_clear()


def _v4(address: str) -> CachedIPv4Address:
    result = ci.cached_ip_addresses(address)
    assert isinstance(result, CachedIPv4Address)
    return result


def _v6(address: str) -> CachedIPv6Address:
    result = ci.cached_ip_addresses(address)
    assert isinstance(result, CachedIPv6Address)
    return result


# ---------------------------------------------------------------------------
# Inheritance & isinstance
# ---------------------------------------------------------------------------


def test_cached_ipv4_is_stdlib_ipv4_subclass() -> None:
    """Subclass check must hold so downstream typing/dispatch keeps working."""
    cached = _v4("10.0.0.1")
    assert isinstance(cached, IPv4Address)
    assert isinstance(cached, CachedIPv4Address)


def test_cached_ipv6_is_stdlib_ipv6_subclass() -> None:
    """Subclass check on the v6 side."""
    cached = _v6("2001:db8::1")
    assert isinstance(cached, IPv6Address)
    assert isinstance(cached, CachedIPv6Address)


# ---------------------------------------------------------------------------
# Symmetric equality with stdlib instances
# ---------------------------------------------------------------------------

_V4_ADDRS = [
    "0.0.0.0",  # noqa: S104
    "127.0.0.1",
    "10.0.0.1",
    "192.168.1.1",
    "8.8.8.8",
    "169.254.0.1",
]
_V6_ADDRS = [
    "::",
    "::1",
    "fe80::1",
    "2001:db8::1",
    "2606:2800:220:1:248:1893:25c8:1946",
]


@pytest.mark.parametrize("address", _V4_ADDRS)
def test_eq_symmetric_with_stdlib_ipv4(address: str) -> None:
    """Equality must be symmetric across CachedIPv4 and stdlib IPv4."""
    cached = _v4(address)
    stdlib = IPv4Address(address)
    assert cached == stdlib
    assert stdlib == cached
    assert not (cached != stdlib)
    assert not (stdlib != cached)


@pytest.mark.parametrize("address", _V6_ADDRS)
def test_eq_symmetric_with_stdlib_ipv6(address: str) -> None:
    """Equality must be symmetric across CachedIPv6 and stdlib IPv6."""
    cached = _v6(address)
    stdlib = IPv6Address(address)
    assert cached == stdlib
    assert stdlib == cached
    assert not (cached != stdlib)
    assert not (stdlib != cached)


def test_v4_not_equal_to_v6_even_when_int_equal() -> None:
    """Cached objects must inherit stdlib's cross-family inequality."""
    cached_v4 = _v4("0.0.0.1")
    cached_v6 = _v6("::1")
    assert int(cached_v4) == int(cached_v6) == 1
    assert cached_v4 != cached_v6
    assert cached_v6 != cached_v4
    assert cached_v4 != IPv6Address("::1")
    assert cached_v6 != IPv4Address("0.0.0.1")


# ---------------------------------------------------------------------------
# Hash compatibility: set membership & dict lookup
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("address", _V4_ADDRS + _V6_ADDRS)
def test_hash_matches_stdlib(address: str) -> None:
    """Cached hash must equal stdlib hash for the same address."""
    cached = ci.cached_ip_addresses(address)
    assert cached is not None
    stdlib = stdlib_ipaddress.ip_address(address)
    assert hash(cached) == hash(stdlib)


def test_cached_dedupes_against_stdlib_in_set() -> None:
    """Mixing cached + stdlib in a set must collapse to one element per address."""
    cached_v4 = _v4("10.0.0.1")
    cached_v6 = _v6("2001:db8::1")
    stdlib_v4 = IPv4Address("10.0.0.1")
    stdlib_v6 = IPv6Address("2001:db8::1")
    bucket: set[IPv4Address | IPv6Address] = {
        cached_v4,
        stdlib_v4,
        cached_v6,
        stdlib_v6,
    }
    assert len(bucket) == 2


def test_dict_lookup_works_across_cached_and_stdlib() -> None:
    """Dicts keyed by stdlib must be queryable with a cached instance, and back."""
    cached = _v4("10.0.0.1")
    stdlib = IPv4Address("10.0.0.1")
    by_stdlib: dict[IPv4Address, str] = {stdlib: "value"}
    by_cached: dict[IPv4Address, str] = {cached: "value"}
    assert by_stdlib[cached] == "value"
    assert by_cached[stdlib] == "value"


# ---------------------------------------------------------------------------
# Ordering: sortable, mixed with stdlib
# ---------------------------------------------------------------------------


def test_sortable_v4_mixed_with_stdlib() -> None:
    """sorted() must work and produce numeric order across cached + stdlib."""
    mix: list[IPv4Address] = [
        _v4("10.0.0.3"),
        IPv4Address("10.0.0.1"),
        _v4("10.0.0.2"),
        IPv4Address("10.0.0.4"),
    ]
    ordered = sorted(mix)
    assert [str(x) for x in ordered] == [
        "10.0.0.1",
        "10.0.0.2",
        "10.0.0.3",
        "10.0.0.4",
    ]


def test_sortable_v6_mixed_with_stdlib() -> None:
    """Same for IPv6."""
    mix: list[IPv6Address] = [
        _v6("2001:db8::3"),
        IPv6Address("2001:db8::1"),
        _v6("2001:db8::2"),
    ]
    ordered = sorted(mix)
    assert [str(x) for x in ordered] == [
        "2001:db8::1",
        "2001:db8::2",
        "2001:db8::3",
    ]


def test_v4_vs_v6_comparison_raises_typeerror() -> None:
    """Stdlib raises TypeError when ordering across families; cached must too."""
    cached_v4 = _v4("10.0.0.1")
    cached_v6 = _v6("::1")
    with pytest.raises(TypeError):
        _ = cached_v4 < cached_v6  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = cached_v6 < cached_v4  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = cached_v4 < IPv6Address("::1")  # type: ignore[operator]


# ---------------------------------------------------------------------------
# Network membership and construction
# ---------------------------------------------------------------------------


def test_cached_in_ipv4_network() -> None:
    """`in` operator on IPv4Network must work for cached instances."""
    cached = _v4("10.0.0.5")
    assert cached in IPv4Network("10.0.0.0/8")
    assert cached not in IPv4Network("192.168.0.0/16")


def test_cached_in_ipv6_network() -> None:
    """`in` operator on IPv6Network must work for cached instances."""
    cached = _v6("2001:db8::1")
    assert cached in IPv6Network("2001:db8::/32")
    assert cached not in IPv6Network("fe80::/10")


def test_network_constructible_from_cached() -> None:
    """IPv4Network/IPv6Network must accept a cached instance as the address arg."""
    cached_v4 = _v4("10.0.0.1")
    net4 = IPv4Network(cached_v4)
    assert net4.network_address == IPv4Address("10.0.0.1")
    assert net4.prefixlen == 32

    cached_v6 = _v6("2001:db8::1")
    net6 = IPv6Network(cached_v6)
    assert net6.network_address == IPv6Address("2001:db8::1")
    assert net6.prefixlen == 128


def test_cached_in_hosts_iterator() -> None:
    """Hosts iterator yields stdlib instances; cached must compare equal to one."""
    cached = _v4("10.0.0.1")
    hosts = list(IPv4Network("10.0.0.0/30").hosts())
    assert cached in hosts


# ---------------------------------------------------------------------------
# Round-trip and conversion compatibility
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("address", _V4_ADDRS + _V6_ADDRS)
def test_str_roundtrip_through_stdlib(address: str) -> None:
    """str(cached) fed back into stdlib must yield an equal address."""
    cached = ci.cached_ip_addresses(address)
    assert cached is not None
    rebuilt = stdlib_ipaddress.ip_address(str(cached))
    assert rebuilt == cached
    assert cached == rebuilt


@pytest.mark.parametrize("address", _V4_ADDRS + _V6_ADDRS)
def test_int_roundtrip_through_stdlib(address: str) -> None:
    """int(cached) fed back into stdlib must yield an equal address."""
    cached = ci.cached_ip_addresses(address)
    assert cached is not None
    family_ctor = IPv4Address if "." in address else IPv6Address
    rebuilt = family_ctor(int(cached))
    assert rebuilt == cached


@pytest.mark.parametrize("address", _V4_ADDRS + _V6_ADDRS)
def test_packed_bytes_match_stdlib(address: str) -> None:
    """Packed-bytes form must match stdlib byte-for-byte."""
    cached = ci.cached_ip_addresses(address)
    assert cached is not None
    stdlib = stdlib_ipaddress.ip_address(address)
    assert cached.packed == stdlib.packed


def test_format_spec_delegates_to_stdlib() -> None:
    """format(cached) and format(cached, 'b') must match stdlib output."""
    cached_v4 = _v4("10.0.0.1")
    stdlib_v4 = IPv4Address("10.0.0.1")
    assert format(cached_v4) == format(stdlib_v4)
    assert format(cached_v4, "b") == format(stdlib_v4, "b")
    assert f"{cached_v4}" == f"{stdlib_v4}"
