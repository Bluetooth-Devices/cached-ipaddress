"""benchmarks for cached_ipaddress.ipaddress."""

from pytest_codspeed import BenchmarkFixture

from cached_ipaddress import ipaddress


def test_eq_performance_miss(benchmark: BenchmarkFixture) -> None:
    ip1 = ipaddress.cached_ip_addresses("127.0.0.1")
    ip2 = ipaddress.cached_ip_addresses("127.0.0.2")

    @benchmark
    def bench() -> None:
        ip1 == ip2  # noqa: B015


def test_eq_performance_hit(benchmark: BenchmarkFixture) -> None:
    ip1 = ipaddress.cached_ip_addresses("127.0.0.1")
    ip2 = ipaddress.cached_ip_addresses("127.0.0.2")

    @benchmark
    def bench() -> None:
        ip1 == ip2  # noqa: B015


def test_is_private_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("10.0.0.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_private  # noqa: B018


def test_is_private_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("fc00::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_private  # noqa: B018


def test_is_global_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("8.8.8.8")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_global  # noqa: B018


def test_is_reserved_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("240.0.0.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_reserved  # noqa: B018


def test_hash_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("127.0.0.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        hash(ip)
