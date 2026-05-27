"""Unit tests for cached_ipaddress.ipaddress."""

import ipaddress as stdlib_ipaddress
from ipaddress import IPv4Address, IPv6Address

import pytest

from cached_ipaddress import ipaddress


def test_cached_ip_addresses_wrapper():
    """Test the cached_ip_addresses_wrapper."""
    assert ipaddress.cached_ip_addresses("") is None
    assert ipaddress.cached_ip_addresses("foo") is None
    assert (
        str(
            ipaddress.cached_ip_addresses(
                b"&\x06(\x00\x02 \x00\x01\x02H\x18\x93%\xc8\x19F"
            )
        )
        == "2606:2800:220:1:248:1893:25c8:1946"
    )
    assert ipaddress.cached_ip_addresses("::1") == ipaddress.IPv6Address("::1")

    ipv4 = ipaddress.cached_ip_addresses("169.254.0.0")
    assert ipv4 is not None
    assert ipv4.is_link_local is True
    assert ipv4.is_unspecified is False
    assert ipv4.is_loopback is False
    assert str(ipv4) == "169.254.0.0"
    assert str(ipv4) == "169.254.0.0"
    assert ipv4.reverse_pointer == "0.0.254.169.in-addr.arpa"

    ipv4 = ipaddress.cached_ip_addresses("0.0.0.0")  # noqa: S104
    assert ipv4 is not None
    assert ipv4.is_link_local is False
    assert ipv4.is_unspecified is True
    assert ipv4.is_loopback is False
    assert ipv4.is_multicast is False
    assert ipv4.compressed == IPv4Address(str(ipv4)).compressed

    ipv6 = ipaddress.cached_ip_addresses("fe80::1")
    assert ipv6 is not None
    assert ipv6.is_link_local is True
    assert ipv6.is_unspecified is False
    assert ipv6.is_loopback is False
    assert ipv6.is_multicast is False
    assert (
        ipv6.reverse_pointer
        == "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.e.f.ip6.arpa"
    )

    ipv6 = ipaddress.cached_ip_addresses("0:0:0:0:0:0:0:0")
    assert ipv6 is not None
    assert ipv6.is_link_local is False
    assert ipv6.is_unspecified is True
    assert ipv6.is_loopback is False
    assert str(ipv6) == "::"

    assert hash(ipv4) == hash(IPv4Address(str(ipv4)))
    assert hash(ipv6) == hash(IPv6Address(str(ipv6)))
    assert int(ipv4) == int(IPv4Address(str(ipv4)))
    assert int(ipv6) == int(IPv6Address(str(ipv6)))
    assert ipv6.compressed == IPv6Address(str(ipv6)).compressed


# A spread of addresses covering private, global, reserved, loopback,
# link-local, multicast and unspecified ranges for both families.
_ADDRESSES = [
    "0.0.0.0",  # noqa: S104
    "127.0.0.1",
    "8.8.8.8",
    "10.0.0.1",
    "172.16.5.4",
    "192.168.1.1",
    "100.64.0.1",
    "169.254.0.1",
    "224.0.0.1",
    "240.0.0.1",
    "::",
    "::1",
    "fe80::1",
    "fc00::1",
    "2001:db8::1",
    "2606:2800:220:1:248:1893:25c8:1946",
    "ff02::1",
]

_BOOL_PROPERTIES = [
    "is_private",
    "is_global",
    "is_reserved",
    "is_link_local",
    "is_loopback",
    "is_multicast",
    "is_unspecified",
]


@pytest.mark.parametrize("address", _ADDRESSES)
def test_properties_match_stdlib(address: str) -> None:
    """Cached objects must report the same values as the stdlib ipaddress."""
    cached = ipaddress.cached_ip_addresses(address)
    expected = stdlib_ipaddress.ip_address(address)
    assert cached is not None

    for prop in _BOOL_PROPERTIES:
        assert getattr(cached, prop) == getattr(expected, prop), prop
    assert cached.reverse_pointer == expected.reverse_pointer
    assert cached.compressed == expected.compressed
    assert cached.exploded == expected.exploded
    assert str(cached) == str(expected)
    assert hash(cached) == hash(expected)
    assert int(cached) == int(expected)
    assert cached == expected


@pytest.mark.parametrize("address", _ADDRESSES)
def test_cached_values_are_stable(address: str) -> None:
    """Repeated access returns identical, stable results."""
    cached = ipaddress.cached_ip_addresses(address)
    assert cached is not None

    # Two reads of every cached attribute must agree with each other.
    for prop in (*_BOOL_PROPERTIES, "reverse_pointer", "compressed", "exploded"):
        assert getattr(cached, prop) == getattr(cached, prop), prop
    assert hash(cached) == hash(cached)
    assert int(cached) == int(cached)
    assert str(cached) == str(cached)


def test_hash_is_cached_on_instance() -> None:
    """The builtin hash() must memoize the result on the instance."""
    # The historical implementation assigned ``self.__hash__`` inside
    # ``__init__``; Python looks up dunders on the type, so ``hash(obj)``
    # never consulted that cache. Guard against the regression by asserting
    # the value is memoized into the instance ``__dict__``.
    #
    # The factory is an ``@lru_cache`` singleton, so clear it first to
    # guarantee a fresh instance regardless of what other tests constructed.
    ipaddress._cached_ip_addresses.cache_clear()
    cached = ipaddress.cached_ip_addresses("8.8.4.4")
    assert cached is not None
    assert "_hash" not in cached.__dict__
    first = hash(cached)
    assert "_hash" in cached.__dict__
    assert first == cached.__dict__["_hash"]
    assert hash(cached) == first == hash(IPv4Address("8.8.4.4"))
