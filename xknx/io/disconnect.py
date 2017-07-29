"""
Abstraction to send DisconnectRequest and wait for DisconnectResponse.
"""
from xknx.knxip import KNXIPServiceType, KNXIPFrame, HPAI,\
    DisconnectResponse
from .request_response import RequestResponse

class Disconnect(RequestResponse):
    """Class to send a DisconnectRequest and wait for a DisconnectResponse."""

    def __init__(self, xknx, udp_client, communication_channel_id):
        self.xknx = xknx
        self.udp_client = udp_client

        super(Disconnect, self).__init__(self.xknx, self.udp_client, DisconnectResponse)

        self.communication_channel_id = communication_channel_id


    def create_knxipframe(self):
        """Create KNX/IP Frame object to be sent to device."""
        (local_addr, local_port) = self.udpclient.getsockname()
        knxipframe = KNXIPFrame()
        knxipframe.init(KNXIPServiceType.DISCONNECT_REQUEST)
        knxipframe.body.communication_channel_id = \
            self.communication_channel_id
        knxipframe.body.control_endpoint = HPAI(
            ip_addr=local_addr, port=local_port)

        return knxipframe
