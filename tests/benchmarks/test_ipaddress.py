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
