import re

from redshift_connector.utils import DriverInfo


def test_version_is_not_none() -> None:
    assert DriverInfo.version() is not None


def test_version_is_str() -> None:
    assert isinstance(DriverInfo.version(), str)


def test_version_proper_format() -> None:
    version_regex: re.Pattern = re.compile(r"^\d+(\.\d+){2,3}$")
    assert version_regex.match(DriverInfo.version())


def test_driver_name_is_not_none() -> None:
    assert DriverInfo.driver_name() is not None


def test_driver_short_name_is_not_none() -> None:
    assert DriverInfo.driver_short_name() is not None


def test_driver_full_name_is_not_none() -> None:
    assert DriverInfo.driver_full_name() is not None


def test_driver_full_name_contains_name() -> None:
    assert DriverInfo.driver_name() in DriverInfo.driver_full_name()


def test_driver_full_name_contains_version() -> None:
    assert DriverInfo.version() in DriverInfo.driver_full_name()
