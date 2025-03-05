"""Build optional cython modules."""

import logging
import os
from distutils.command.build_ext import build_ext
from typing import Any

try:
    from setuptools import Extension
except ImportError:
    from distutils.core import Extension

TO_CYTHONIZE = ["src/cached_ipaddress/ipaddress.py"]

EXTENSIONS = [
    Extension(
        ext.removeprefix("src/").removesuffix(".py").replace("/", "."),
        [ext],
        language="c",
        extra_compile_args=["-O3", "-g0"],
    )
    for ext in TO_CYTHONIZE
]


_LOGGER = logging.getLogger(__name__)


class BuildExt(build_ext):
    """BuildExt."""

    def build_extensions(self) -> None:
        """Build extensions."""
        try:
            super().build_extensions()
        except Exception:
            _LOGGER.debug("Failed to build extensions", exc_info=True)
            pass


def build(setup_kwargs: Any) -> None:
    """Build optional cython modules."""
    if os.environ.get("SKIP_CYTHON", False):
        return
    try:
        from Cython.Build import cythonize

        setup_kwargs.update(
            {
                "ext_modules": cythonize(
                    EXTENSIONS,
                    compiler_directives={"language_level": "3"},  # Python 3
                ),
                "cmdclass": {"build_ext": BuildExt},
            }
        )
        setup_kwargs["exclude_package_data"] = {
            pkg: ["*.c"] for pkg in setup_kwargs["packages"]
        }
    except Exception:
        if os.environ.get("REQUIRE_CYTHON"):
            raise
        pass
