"""Unit test for KNX/IP DisconnectRequest objects."""
import pytest

from xknx import XKNX
from xknx.exceptions import CouldNotParseKNXIP
from xknx.knxip import HPAI, DisconnectRequest, KNXIPFrame


class TestKNXIPDisconnectRequest:
    """Test class for KNX/IP DisconnectRequest objects."""

    def test_disconnect_request(self):
        """Test parsing and streaming DisconnectRequest KNX/IP packet."""
        raw = bytes.fromhex("06 10 02 09 00 10 15 00 08 01 C0 A8 C8 0C C3 B4")
        xknx = XKNX()
        knxipframe = KNXIPFrame(xknx)
        knxipframe.from_knx(raw)

        assert isinstance(knxipframe.body, DisconnectRequest)

        assert knxipframe.body.communication_channel_id == 21
        assert knxipframe.body.control_endpoint == HPAI(
            ip_addr="192.168.200.12", port=50100
        )

        disconnect_request = DisconnectRequest(
            xknx,
            communication_channel_id=21,
            control_endpoint=HPAI(ip_addr="192.168.200.12", port=50100),
        )
        knxipframe2 = KNXIPFrame.init_from_body(disconnect_request)

        assert knxipframe2.to_knx() == raw

    def test_from_knx_wrong_length(self):
        """Test parsing and streaming wrong DisconnectRequest."""
        raw = bytes((0x06, 0x10, 0x02, 0x09, 0x00, 0x10))
        xknx = XKNX()
        knxipframe = KNXIPFrame(xknx)
        with pytest.raises(CouldNotParseKNXIP):
            knxipframe.from_knx(raw)
