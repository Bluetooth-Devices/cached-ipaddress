"""Base implementation."""

from functools import lru_cache
from ipaddress import AddressValueError, IPv4Address, IPv6Address, NetmaskValueError

from ._compat import cached_property


class CachedIPv4Address(IPv4Address):

    def __hash__(self) -> int:
        """Return the cached hash of the IPv4 address."""
        return self._hash

    @cached_property
    def _hash(self) -> int:
        """Return the hash of the IPv4 address."""
        return super().__hash__()

    def __str__(self) -> str:
        """Return the string representation of the IPv4 address."""
        return self._str

    @cached_property
    def _str(self) -> str:
        """Return the string representation of the IPv4 address."""
        return super().__str__()

    @cached_property
    def is_link_local(self) -> bool:
        """Return True if this is a link-local address."""
        return super().is_link_local

    @cached_property
    def is_unspecified(self) -> bool:
        """Return True if this is an unspecified address."""
        return super().is_unspecified

    @cached_property
    def is_loopback(self) -> bool:
        """Return True if this is a loopback address."""
        return super().is_loopback

    @cached_property
    def is_multicast(self) -> bool:
        """Return True if this is a multicast address."""
        return super().is_multicast

    @cached_property
    def is_private(self) -> bool:
        """Return True if this is a private address."""
        return super().is_private

    @cached_property
    def is_global(self) -> bool:
        """Return True if this is a global address."""
        return super().is_global

    @cached_property
    def is_reserved(self) -> bool:
        """Return True if this is a reserved address."""
        return super().is_reserved

    @cached_property
    def reverse_pointer(self) -> str:
        """Return the reverse DNS pointer name for the IPv4 address."""
        return super().reverse_pointer

    @cached_property
    def compressed(self) -> str:
        """Return the compressed value IPv4 address."""
        return super().compressed

    @cached_property
    def exploded(self) -> str:
        """Return the exploded form of the IPv4 address."""
        return super().exploded

    @cached_property
    def packed(self) -> bytes:
        """Return the packed binary form of the IPv4 address."""
        return super().packed


class CachedIPv6Address(IPv6Address):

    def __hash__(self) -> int:
        """Return the cached hash of the IPv6 address."""
        return self._hash

    @cached_property
    def _hash(self) -> int:
        """Return the hash of the IPv6 address."""
        return super().__hash__()

    def __str__(self) -> str:
        """Return the string representation of the IPv6 address."""
        return self._str

    @cached_property
    def _str(self) -> str:
        """Return the string representation of the IPv6 address."""
        return super().__str__()

    @cached_property
    def is_link_local(self) -> bool:
        """Return True if this is a link-local address."""
        return super().is_link_local

    @cached_property
    def is_unspecified(self) -> bool:
        """Return True if this is an unspecified address."""
        return super().is_unspecified

    @cached_property
    def is_loopback(self) -> bool:
        """Return True if this is a loopback address."""
        return super().is_loopback

    @cached_property
    def is_multicast(self) -> bool:
        """Return True if this is a multicast address."""
        return super().is_multicast

    @cached_property
    def is_private(self) -> bool:
        """Return True if this is a private address."""
        return super().is_private

    @cached_property
    def is_global(self) -> bool:
        """Return True if this is a global address."""
        return super().is_global

    @cached_property
    def is_reserved(self) -> bool:
        """Return True if this is a reserved address."""
        return super().is_reserved

    @cached_property
    def reverse_pointer(self) -> str:
        """Return the reverse DNS pointer name for the IPv6 address."""
        return super().reverse_pointer

    @cached_property
    def compressed(self) -> str:
        """Return the compressed value IPv6 address."""
        return super().compressed

    @cached_property
    def exploded(self) -> str:
        """Return the exploded form of the IPv6 address."""
        return super().exploded

    @cached_property
    def packed(self) -> bytes:
        """Return the packed binary form of the IPv6 address."""
        return super().packed

    @cached_property
    def is_site_local(self) -> bool:
        """Return True if this is a site-local address."""
        return super().is_site_local

    @cached_property
    def ipv4_mapped(self) -> IPv4Address | None:
        """Return the IPv4-mapped address, or None if not an IPv4-mapped address."""
        return super().ipv4_mapped

    @cached_property
    def sixtofour(self) -> IPv4Address | None:
        """Return the embedded IPv4 address of a 6to4 address, or None."""
        return super().sixtofour

    @cached_property
    def teredo(self) -> tuple[IPv4Address, IPv4Address] | None:
        """Return the Teredo (server, client) IPv4 tuple, or None."""
        return super().teredo


@lru_cache(maxsize=535)
def _cached_ip_addresses(
    address: str | bytes | int,
) -> IPv4Address | IPv6Address | None:
    """Cache IP addresses."""
    try:
        return CachedIPv4Address(address)
    except (AddressValueError, NetmaskValueError):
        pass

    try:
        return CachedIPv6Address(address)
    except (AddressValueError, NetmaskValueError):
        return None


cached_ip_addresses_wrapper = _cached_ip_addresses
cached_ip_addresses = cached_ip_addresses_wrapper

__all__ = ("cached_ip_addresses",)
