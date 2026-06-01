"""Construction (cache-miss) benchmarks for cached_ipaddress.ipaddress."""

from pytest_codspeed import BenchmarkFixture

from cached_ipaddress import ipaddress


def test_construction_miss_ipv4_string(benchmark: BenchmarkFixture) -> None:
    addresses = [f"10.0.{i // 256}.{i % 256}" for i in range(400)]
    cache_clear = ipaddress._cached_ip_addresses.cache_clear

    @benchmark
    def bench() -> None:
        cache_clear()
        for addr in addresses:
            ipaddress.cached_ip_addresses(addr)


def test_construction_miss_ipv6_string(benchmark: BenchmarkFixture) -> None:
    addresses = [f"2001:db8::{i:x}" for i in range(400)]
    cache_clear = ipaddress._cached_ip_addresses.cache_clear

    @benchmark
    def bench() -> None:
        cache_clear()
        for addr in addresses:
            ipaddress.cached_ip_addresses(addr)


def test_construction_miss_invalid_string(benchmark: BenchmarkFixture) -> None:
    addresses = [f"not-an-ip-{i}" for i in range(400)]
    cache_clear = ipaddress._cached_ip_addresses.cache_clear

    @benchmark
    def bench() -> None:
        cache_clear()
        for addr in addresses:
            ipaddress.cached_ip_addresses(addr)
