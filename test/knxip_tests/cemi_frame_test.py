"""Tests for the CEMIFrame object."""
from unittest.mock import MagicMock

from pytest import fixture, raises

from xknx.dpt import DPTBinary
from xknx.exceptions import ConversionError, CouldNotParseKNXIP, UnsupportedCEMIMessage
from xknx.knxip.cemi_frame import CEMIFrame
from xknx.knxip.knxip_enum import CEMIFlags, CEMIMessageCode
from xknx.telegram import GroupAddress, IndividualAddress, Telegram
from xknx.telegram.apci import GroupValueRead


def get_data(code, adil, flags, src, dst, mpdu_len, tpci_apci, payload):
    """Encode to cemi data raw bytes."""
    return bytes(
        [
            code,
            adil,  # adil
            (flags >> 8) & 255,  # flags
            flags & 255,  # flags
            (src >> 8) & 255,  # src
            src & 255,  # src
            (dst >> 8) & 255,  # dst
            dst & 255,  # dst
            mpdu_len,  # mpdu_len
            (tpci_apci >> 8) & 255,  # tpci_apci
            tpci_apci & 255,  # tpci_apci
            *payload,  # payload
        ]
    )


@fixture(name="frame")
def fixture_frame():
    """Fixture to get a simple mocked frame."""
    xknx = MagicMock()
    return CEMIFrame(xknx)


def test_valid_command(frame):
    """Test for valid frame parsing."""
    packet_len = frame.from_knx(get_data(0x29, 0, 0, 0, 0, 1, 0, []))
    assert frame.code == CEMIMessageCode.L_DATA_IND
    assert frame.flags == 0
    assert frame.mpdu_len == 1
    assert frame.payload == GroupValueRead()
    assert frame.src_addr == IndividualAddress(0)
    assert frame.dst_addr == IndividualAddress(0)
    assert packet_len == 11


def test_invalid_tpci_apci(frame):
    """Test for invalid APCIService."""
    with raises(UnsupportedCEMIMessage, match=r".*APCI not supported: .*"):
        frame.from_knx_data_link_layer(get_data(0x29, 0, 0, 0, 0, 1, 0xFFC0, []))


def test_invalid_apdu_len(frame):
    """Test for invalid apdu len."""
    with raises(CouldNotParseKNXIP, match=r".*APDU LEN should be .*"):
        frame.from_knx(get_data(0x29, 0, 0, 0, 0, 2, 0, []))


def test_invalid_src_addr(frame):
    """Test for invalid src addr."""
    frame.code = CEMIMessageCode.L_DATA_IND
    frame.flags = 0
    frame.mpdu_len = 1
    frame.payload = GroupValueRead()
    frame.src_addr = None
    frame.dst_addr = IndividualAddress(0)

    with raises(ConversionError, match=r"src_addr not set"):
        frame.to_knx()


def test_invalid_dst_addr(frame):
    """Test for invalid dst addr."""
    frame.code = CEMIMessageCode.L_DATA_IND
    frame.flags = 0
    frame.mpdu_len = 1
    frame.payload = GroupValueRead()
    frame.src_addr = IndividualAddress(0)
    frame.dst_addr = None

    with raises(ConversionError, match=r"dst_addr not set"):
        frame.to_knx()


def test_invalid_payload(frame):
    """Test for having wrong payload set."""
    frame.code = CEMIMessageCode.L_DATA_IND
    frame.flags = 0
    frame.mpdu_len = 1
    frame.payload = DPTBinary(1)
    frame.src_addr = IndividualAddress(0)
    frame.dst_addr = IndividualAddress(0)

    with raises(TypeError):
        frame.calculated_length()

    with raises(TypeError):
        frame.to_knx()


def test_from_knx_with_not_handleable_cemi(frame):
    """Test for having unhandlebale cemi set."""
    with raises(UnsupportedCEMIMessage, match=r".*CEMIMessageCode not implemented:.*"):
        frame.from_knx(get_data(0x30, 0, 0, 0, 0, 2, 0, []))


def test_from_knx_with_not_implemented_cemi(frame):
    """Test for having not implemented CEMI set."""
    with raises(UnsupportedCEMIMessage, match=r".*Could not handle CEMIMessageCode:.*"):
        frame.from_knx(
            get_data(CEMIMessageCode.L_BUSMON_IND.value, 0, 0, 0, 0, 2, 0, [])
        )


def test_invalid_invalid_len(frame):
    """Test for invalid cemi len."""
    with raises(UnsupportedCEMIMessage, match=r".*CEMI too small.*"):
        frame.from_knx_data_link_layer(get_data(0x29, 0, 0, 0, 0, 2, 0, [])[:5])


def test_from_knx_group_address(frame):
    """Test conversion for a cemi with a group address as destination."""
    frame.from_knx(get_data(0x29, 0, 0x80, 0, 0, 1, 0, []))

    assert frame.dst_addr == GroupAddress(0)


def test_from_knx_individual_address(frame):
    """Test conversion for a cemi with a individual address as destination."""
    frame.from_knx(get_data(0x29, 0, 0x00, 0, 0, 1, 0, []))

    assert frame.dst_addr == IndividualAddress(0)


def test_telegram_group_address(frame):
    """Test telegram conversion flags with a group address."""
    frame.telegram = Telegram(destination_address=GroupAddress(0))

    assert (
        frame.flags & CEMIFlags.DESTINATION_GROUP_ADDRESS
    ) == CEMIFlags.DESTINATION_GROUP_ADDRESS


def test_telegram_individual_address(frame):
    """Test telegram conversion flags with a individual address."""
    frame.telegram = Telegram(destination_address=IndividualAddress(0))

    assert (
        frame.flags & CEMIFlags.DESTINATION_INDIVIDUAL_ADDRESS
    ) == CEMIFlags.DESTINATION_INDIVIDUAL_ADDRESS


def test_telegram_unsupported_address(frame):
    """Test telegram conversion flags with an unsupported address."""
    with raises(TypeError):
        frame.telegram = Telegram(destination_address=object())
