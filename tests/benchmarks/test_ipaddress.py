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


def test_is_global_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("2001:db8::1")
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


def test_is_reserved_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("2001:db8::1")
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


def test_hash_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("2001:db8::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        hash(ip)


def test_is_loopback_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("127.0.0.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_loopback  # noqa: B018


def test_is_loopback_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_loopback  # noqa: B018


def test_is_link_local_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("169.254.0.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_link_local  # noqa: B018


def test_is_link_local_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("fe80::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_link_local  # noqa: B018


def test_is_unspecified_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("0.0.0.0")  # noqa: S104
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_unspecified  # noqa: B018


def test_is_unspecified_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("::")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_unspecified  # noqa: B018


def test_is_multicast_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("224.0.0.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_multicast  # noqa: B018


def test_is_multicast_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("ff02::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.is_multicast  # noqa: B018


def test_str_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("192.0.2.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        str(ip)


def test_str_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("2001:db8::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        str(ip)


def test_exploded_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("192.0.2.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.exploded  # noqa: B018


def test_exploded_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("2001:db8::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.exploded  # noqa: B018


def test_compressed_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("192.0.2.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.compressed  # noqa: B018


def test_compressed_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("2001:db8::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.compressed  # noqa: B018


def test_reverse_pointer_performance(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("192.0.2.1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.reverse_pointer  # noqa: B018


def test_reverse_pointer_performance_ipv6(benchmark: BenchmarkFixture) -> None:
    ip = ipaddress.cached_ip_addresses("2001:db8::1")
    assert ip is not None

    @benchmark
    def bench() -> None:
        ip.reverse_pointer  # noqa: B018


def test_construction_miss_ipv4_string(benchmark: BenchmarkFixture) -> None:
    cache_clear = ipaddress._cached_ip_addresses.cache_clear

    @benchmark
    def bench() -> None:
        cache_clear()
        ipaddress.cached_ip_addresses("192.0.2.1")


def test_construction_miss_ipv6_string(benchmark: BenchmarkFixture) -> None:
    cache_clear = ipaddress._cached_ip_addresses.cache_clear

    @benchmark
    def bench() -> None:
        cache_clear()
        ipaddress.cached_ip_addresses("2001:db8::1")


def test_construction_miss_invalid_string(benchmark: BenchmarkFixture) -> None:
    cache_clear = ipaddress._cached_ip_addresses.cache_clear

    @benchmark
    def bench() -> None:
        cache_clear()
        ipaddress.cached_ip_addresses("not-an-ip")
