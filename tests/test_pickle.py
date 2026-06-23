"""Pickle and copy round-trip contract for cached address classes."""

import copy
import pickle

import pytest

from cached_ipaddress.ipaddress import (
    CachedIPv4Address,
    CachedIPv6Address,
    cached_ip_addresses,
)

_IPV4 = ["0.0.0.0", "127.0.0.1", "192.0.2.1", "8.8.8.8"]  # noqa: S104
_IPV6 = ["::", "::1", "fe80::1", "2001:db8::1"]


@pytest.fixture(autouse=True)
def _clear_factory_cache():
    """Each test starts from a clean LRU so instance identity is predictable."""
    from cached_ipaddress import ipaddress as mod

    mod._cached_ip_addresses.cache_clear()


@pytest.mark.parametrize("address", _IPV4)
@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_roundtrip_preserves_ipv4(address: str, protocol: int) -> None:
    original = cached_ip_addresses(address)
    assert isinstance(original, CachedIPv4Address)
    restored = pickle.loads(pickle.dumps(original, protocol=protocol))  # noqa: S301
    assert type(restored) is CachedIPv4Address
    assert restored == original
    assert hash(restored) == hash(original)
    assert int(restored) == int(original)
    assert str(restored) == str(original)


@pytest.mark.parametrize("address", _IPV6)
@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_roundtrip_preserves_ipv6(address: str, protocol: int) -> None:
    original = cached_ip_addresses(address)
    assert isinstance(original, CachedIPv6Address)
    restored = pickle.loads(pickle.dumps(original, protocol=protocol))  # noqa: S301
    assert type(restored) is CachedIPv6Address
    assert restored == original
    assert hash(restored) == hash(original)
    assert int(restored) == int(original)
    assert str(restored) == str(original)


def test_pickle_does_not_carry_cached_properties() -> None:
    """Restored instances re-cache lazily; the wire format carries no cache state."""
    original = cached_ip_addresses("2001:db8::1")
    assert original is not None
    # Force several caches to populate.
    _ = original.is_private
    _ = original.exploded
    _ = str(original)
    _ = hash(original)
    assert original.__dict__, "sanity: caches should have populated"

    restored = pickle.loads(pickle.dumps(original))  # noqa: S301
    assert restored.__dict__ == {}
    # Re-access works and re-caches.
    assert restored.is_private == original.is_private
    assert restored.exploded == original.exploded
    assert "is_private" in restored.__dict__
    assert "exploded" in restored.__dict__


@pytest.mark.parametrize("address", _IPV4 + _IPV6)
def test_copy_preserves_type_and_equality(address: str) -> None:
    original = cached_ip_addresses(address)
    assert original is not None
    duplicate = copy.copy(original)
    assert type(duplicate) is type(original)
    assert duplicate == original
    assert hash(duplicate) == hash(original)


@pytest.mark.parametrize("address", _IPV4 + _IPV6)
def test_deepcopy_preserves_type_and_equality(address: str) -> None:
    original = cached_ip_addresses(address)
    assert original is not None
    duplicate = copy.deepcopy(original)
    assert type(duplicate) is type(original)
    assert duplicate == original
    assert hash(duplicate) == hash(original)


def test_pickled_instances_are_set_dict_compatible() -> None:
    """Restored instances remain interchangeable in hash-based containers."""
    addrs = [cached_ip_addresses(a) for a in _IPV4 + _IPV6]
    restored = [pickle.loads(pickle.dumps(a)) for a in addrs]  # noqa: S301
    combined = {*addrs, *restored}
    assert len(combined) == len(addrs)
    for original, again in zip(addrs, restored, strict=True):
        assert original in combined
        assert again in combined
