"""Unit test for Address class."""
import pytest

from xknx.exceptions import CouldNotParseAddress
from xknx.telegram.address import (
    GroupAddress,
    GroupAddressType,
    IndividualAddress,
    InternalGroupAddress,
    parse_device_group_address,
)

group_addresses_valid = {
    "0/0": 0,
    "0/1": 1,
    "0/11": 11,
    "0/111": 111,
    "0/1111": 1111,
    "0/2047": 2047,
    "0/0/0": 0,
    "0/0/1": 1,
    "0/0/11": 11,
    "0/0/111": 111,
    "0/0/255": 255,
    "0/1/11": 267,
    "0/1/111": 367,
    "0/7/255": 2047,
    "1/0": 2048,
    "1/0/0": 2048,
    "1/1/111": 2415,
    "1/7/255": 4095,
    "31/7/255": 65535,
    "1": 1,
    0: 0,
    65535: 65535,
    (0xFF, 0xFF): 65535,
    GroupAddress("1/1/111"): 2415,
    None: 0,
}

group_addresses_invalid = [
    "0/2049",
    "0/8/0",
    "0/0/256",
    "32/0",
    "0/0a",
    "a0/0",
    "abc",
    "1.1.1",
    "0.0",
    IndividualAddress("11.11.111"),
    65536,
    (0xFF, 0xFFF),
    (0xFFF, 0xFF),
    (-1, -1),
    [],
]

individual_addresses_valid = {
    "0.0.0": 0,
    "123": 123,
    "1.0.0": 4096,
    "1.1.0": 4352,
    "1.1.1": 4353,
    "1.1.11": 4363,
    "1.1.111": 4463,
    "1.11.111": 7023,
    "11.11.111": 47983,
    IndividualAddress("11.11.111"): 47983,
    "15.15.255": 65535,
    (0xFF, 0xFF): 65535,
    0: 0,
    65535: 65535,
}

individual_addresses_invalid = [
    "15.15.256",
    "16.0.0",
    "0.16.0",
    "15.15.255a",
    "a15.15.255",
    "abc",
    "1/1/1",
    "0/0",
    GroupAddress("1/1/111"),
    65536,
    (0xFF, 0xFFF),
    (0xFFF, 0xFF),
    (-1, -1),
    [],
]

internal_group_addresses_valid = {
    "i 123": "123",
    "i-123": "123",
    "i_123": "123",
    "I 123": "123",
    "i abc": "abc",
    "i-abc": "abc",
    "i_abc": "abc",
    "I-abc": "abc",
    "i123": "123",
    "iabc": "abc",
    "IABC": "ABC",
    "i   abc  ": "abc",
    "i asdf 123 adsf ": "asdf 123 adsf",
    "i-1/2/3": "1/2/3",
    InternalGroupAddress("i-123"): "123",
}

internal_group_addresses_invalid = [
    "i",
    "i-",
    "i ",
    "i  ",
    "i- ",
    "a",
]


class TestIndividualAddress:
    """Test class for IndividualAddress."""

    @pytest.mark.parametrize(
        "address_test,address_raw", individual_addresses_valid.items()
    )
    def test_with_valid(self, address_test, address_raw):
        """Test with some valid addresses."""

        assert IndividualAddress(address_test).raw == address_raw

    @pytest.mark.parametrize("address_test", individual_addresses_invalid)
    def test_with_invalid(self, address_test):
        """Test with some invalid addresses."""

        with pytest.raises(CouldNotParseAddress):
            IndividualAddress(address_test)

    def test_with_int(self):
        """Test initialization with free format address as integer."""
        assert IndividualAddress(49552).raw == 49552

    def test_with_bytes(self):
        """Test initialization with Bytes."""
        assert IndividualAddress((0x12, 0x34)).raw == 0x1234

    def test_with_none(self):
        """Test initialization with None object."""
        assert IndividualAddress(None).raw == 0

    def test_is_line(self):
        """Test if `IndividualAddress.is_line` works like excepted."""
        assert IndividualAddress("1.0.0").is_line
        assert not IndividualAddress("1.0.1").is_line

    def test_is_device(self):
        """Test if `IndividualAddress.is_device` works like excepted."""
        assert IndividualAddress("1.0.1").is_device
        assert not IndividualAddress("1.0.0").is_device

    def test_to_knx(self):
        """Test if `IndividualAddress.to_knx()` generates valid byte tuples."""
        assert IndividualAddress("0.0.0").to_knx() == (0x0, 0x0)
        assert IndividualAddress("15.15.255").to_knx() == (0xFF, 0xFF)

    def test_equal(self):
        """Test if the equal operator works in all cases."""
        assert IndividualAddress("1.0.0") == IndividualAddress(4096)
        assert IndividualAddress("1.0.0") != IndividualAddress("1.1.1")
        assert IndividualAddress("1.0.0") is not None
        assert IndividualAddress("1.0.0") != "example"
        assert IndividualAddress("1.1.1") != GroupAddress("1/1/1")
        assert IndividualAddress(250) != GroupAddress(250)
        assert IndividualAddress(250) != 250

    def test_representation(self):
        """Test string representation of address."""
        assert repr(IndividualAddress("2.3.4")) == 'IndividualAddress("2.3.4")'


class TestGroupAddress:
    """Test class for GroupAddress."""

    @pytest.mark.parametrize("address_test,address_raw", group_addresses_valid.items())
    def test_with_valid(self, address_test, address_raw):
        """
        Test if the class constructor generates valid raw values.

        This test checks:
        * all allowed input variants (strings, tuples, integers)
        * for conversation errors
        * for upper/lower limits still working, to avoid off-by-one errors
        """

        assert GroupAddress(address_test).raw == address_raw

    @pytest.mark.parametrize("address_test", group_addresses_invalid)
    def test_with_invalid(self, address_test):
        """
        Test if constructor raises an exception for all known invalid cases.

        Checks:
        * addresses or parts of it too high/low
        * invalid input variants (lists instead of tuples)
        * invalid strings
        """

        with pytest.raises(CouldNotParseAddress):
            GroupAddress(address_test)

    def test_main(self):
        """
        Test if `GroupAddress.main` works.

        Checks:
        * Main group part of a strings returns the right value
        * Return `None` on `GroupAddressType.FREE`
        """
        assert GroupAddress("1/0").main == 1
        assert GroupAddress("15/0").main == 15
        assert GroupAddress("31/0/0").main == 31
        assert GroupAddress("1/0", GroupAddressType.FREE).main is None

    def test_middle(self):
        """
        Test if `GroupAddress.middle` works.

        Checks:
        * Middle group part of a strings returns the right value
        * Return `None` if not `GroupAddressType.LONG`
        """
        assert GroupAddress("1/0/1", GroupAddressType.LONG).middle == 0
        assert GroupAddress("1/7/1", GroupAddressType.LONG).middle == 7
        assert GroupAddress("1/0", GroupAddressType.SHORT).middle is None
        assert GroupAddress("1/0", GroupAddressType.FREE).middle is None

    def test_sub(self):
        """
        Test if `GroupAddress.sub` works.

        Checks:
        * Sub group part of a strings returns the right value
        * Return never `None`
        """
        assert GroupAddress("1/0", GroupAddressType.SHORT).sub == 0
        assert GroupAddress("31/0", GroupAddressType.SHORT).sub == 0
        assert GroupAddress("1/2047", GroupAddressType.SHORT).sub == 2047
        assert GroupAddress("31/2047", GroupAddressType.SHORT).sub == 2047
        assert GroupAddress("1/0/0", GroupAddressType.LONG).sub == 0
        assert GroupAddress("1/0/255", GroupAddressType.LONG).sub == 255
        assert GroupAddress("0/0", GroupAddressType.FREE).sub == 0
        assert GroupAddress("1/0", GroupAddressType.FREE).sub == 2048
        assert GroupAddress("31/2047", GroupAddressType.FREE).sub == 65535

    def test_to_knx(self):
        """Test if `GroupAddress.to_knx()` generates valid byte tuples."""
        assert GroupAddress("0/0").to_knx() == (0x0, 0x0)
        assert GroupAddress("31/2047").to_knx() == (0xFF, 0xFF)

    def test_equal(self):
        """Test if the equal operator works in all cases."""
        assert GroupAddress("1/0") == GroupAddress(2048)
        assert GroupAddress("1/1") != GroupAddress("1/1/0")
        assert GroupAddress("1/0") is not None
        assert GroupAddress("1/0") != "example"
        assert GroupAddress(1) != IndividualAddress(1)
        assert GroupAddress(1) != 1

    def test_representation(self):
        """Test string representation of address."""
        assert repr(GroupAddress("0", GroupAddressType.FREE)) == 'GroupAddress("0")'
        assert repr(GroupAddress("0", GroupAddressType.SHORT)) == 'GroupAddress("0/0")'
        assert repr(GroupAddress("0", GroupAddressType.LONG)) == 'GroupAddress("0/0/0")'


class TestInternalGroupAddress:
    """Test class for InternalGroupAddress."""

    @pytest.mark.parametrize(
        "address_test,address_raw", internal_group_addresses_valid.items()
    )
    def test_with_valid(self, address_test, address_raw):
        """Test if the class constructor generates valid raw values."""

        assert InternalGroupAddress(address_test).address == address_raw

    @pytest.mark.parametrize(
        "address_test",
        [
            *internal_group_addresses_invalid,
            *group_addresses_valid,
            *group_addresses_invalid,
            *individual_addresses_valid,
            *individual_addresses_invalid,
        ],
    )
    def test_with_invalid(self, address_test):
        """Test if constructor raises an exception for all known invalid cases."""

        with pytest.raises(CouldNotParseAddress):
            InternalGroupAddress(address_test)

    def test_equal(self):
        """Test if the equal operator works in all cases."""
        assert InternalGroupAddress("i 123") == InternalGroupAddress("i 123")
        assert InternalGroupAddress("i-asdf") == InternalGroupAddress("i asdf")
        assert InternalGroupAddress("i-asdf") == InternalGroupAddress("Iasdf")
        assert InternalGroupAddress("i-1") != InternalGroupAddress("i-2")
        assert InternalGroupAddress("i-1") is not None
        assert InternalGroupAddress("i-example") != "example"
        assert InternalGroupAddress("i-0") != GroupAddress(0)
        assert InternalGroupAddress("i-1") != IndividualAddress(1)
        assert InternalGroupAddress("i-1") != 1

    def test_representation(self):
        """Test string representation of address."""
        assert repr(InternalGroupAddress("i0")) == 'InternalGroupAddress("i-0")'
        assert repr(InternalGroupAddress("i-0")) == 'InternalGroupAddress("i-0")'
        assert repr(InternalGroupAddress("i 0")) == 'InternalGroupAddress("i-0")'


class TestParseDestinationAddress:
    """Test class for parsing destination addresses."""

    @pytest.mark.parametrize("address_test", group_addresses_valid)
    def test_parse_group_address(self, address_test):
        """Test if the function returns GroupAddress objects."""
        assert isinstance(parse_device_group_address(address_test), GroupAddress)

    @pytest.mark.parametrize("address_test", internal_group_addresses_valid)
    def test_parse_internal_group_address(self, address_test):
        """Test if the function returns InternalGroupAddress objects."""
        assert isinstance(
            parse_device_group_address(address_test), InternalGroupAddress
        )

    @pytest.mark.parametrize(
        "address_test",
        [
            *internal_group_addresses_invalid,
            *group_addresses_invalid,
        ],
    )
    def test_parse_invalid(self, address_test):
        """Test if the function raises CouldNotParseAddress on invalid values."""
        with pytest.raises(CouldNotParseAddress):
            parse_device_group_address(address_test)
