"""
Module for serialization and deserialization of KNX/IP packets.

It consists of a header and a body.
Depending on the service_type_ident different types of body classes are instanciated.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from xknx.exceptions import CouldNotParseKNXIP, IncompleteKNXIPFrame

from .body import KNXIPBody
from .connect_request import ConnectRequest
from .connect_response import ConnectResponse
from .connectionstate_request import ConnectionStateRequest
from .connectionstate_response import ConnectionStateResponse
from .description_request import DescriptionRequest
from .description_response import DescriptionResponse
from .disconnect_request import DisconnectRequest
from .disconnect_response import DisconnectResponse
from .header import KNXIPHeader
from .knxip_enum import KNXIPServiceType
from .routing_indication import RoutingIndication
from .search_request import SearchRequest
from .search_response import SearchResponse
from .tunnelling_ack import TunnellingAck
from .tunnelling_request import TunnellingRequest

if TYPE_CHECKING:
    from xknx.xknx import XKNX


class KNXIPFrame:
    """Class for KNX/IP Frames."""

    def __init__(self, xknx: XKNX):
        """Initialize object."""
        self.xknx = xknx
        self.header = KNXIPHeader()
        self.body: KNXIPBody | None = None

    def init(self, service_type_ident: KNXIPServiceType) -> KNXIPBody:
        """Init object by service_type_ident. Will instanciate a body object depending on service_type_ident."""
        self.header.service_type_ident = service_type_ident

        body: KNXIPBody
        # Core
        if service_type_ident == KNXIPServiceType.SEARCH_REQUEST:
            body = SearchRequest(self.xknx)
        elif service_type_ident == KNXIPServiceType.SEARCH_RESPONSE:
            body = SearchResponse(self.xknx)
        elif service_type_ident == KNXIPServiceType.DESCRIPTION_REQUEST:
            body = DescriptionRequest(self.xknx)
        elif service_type_ident == KNXIPServiceType.DESCRIPTION_RESPONSE:
            body = DescriptionResponse(self.xknx)
        elif service_type_ident == KNXIPServiceType.CONNECT_REQUEST:
            body = ConnectRequest(self.xknx)
        elif service_type_ident == KNXIPServiceType.CONNECT_RESPONSE:
            body = ConnectResponse(self.xknx)
        elif service_type_ident == KNXIPServiceType.CONNECTIONSTATE_REQUEST:
            body = ConnectionStateRequest(self.xknx)
        elif service_type_ident == KNXIPServiceType.CONNECTIONSTATE_RESPONSE:
            body = ConnectionStateResponse(self.xknx)
        elif service_type_ident == KNXIPServiceType.DISCONNECT_REQUEST:
            body = DisconnectRequest(self.xknx)
        elif service_type_ident == KNXIPServiceType.DISCONNECT_RESPONSE:
            body = DisconnectResponse(self.xknx)
        # Tunneling
        elif service_type_ident == KNXIPServiceType.TUNNELLING_REQUEST:
            body = TunnellingRequest(self.xknx)
        elif service_type_ident == KNXIPServiceType.TUNNELLING_ACK:
            body = TunnellingAck(self.xknx)
        # Routing
        elif service_type_ident == KNXIPServiceType.ROUTING_INDICATION:
            body = RoutingIndication(self.xknx)
        else:
            raise CouldNotParseKNXIP(
                f"KNXIPServiceType not implemented: {service_type_ident.name}"
            )
        self.body = body
        return body

    @staticmethod
    def init_from_body(knxip_body: KNXIPBody) -> KNXIPFrame:
        """Return KNXIPFrame from KNXIPBody."""
        knxipframe = KNXIPFrame(knxip_body.xknx)
        knxipframe.header.service_type_ident = knxip_body.__class__.SERVICE_TYPE
        knxipframe.body = knxip_body
        knxipframe.header.set_length(knxip_body)
        return knxipframe

    def from_knx(self, data: bytes) -> int:
        """Parse/deserialize from KNX/IP raw data."""
        pos = self.header.from_knx(data)
        if len(data) < self.header.total_length:
            raise IncompleteKNXIPFrame("Incomplete data for KNXIPFrame")
        # limit data to self.header.total_length for streaming socket data
        self.init(self.header.service_type_ident).from_knx(
            data[pos : self.header.total_length]
        )
        return self.header.total_length

    def to_knx(self) -> bytes:
        """Serialize to KNX/IP raw data."""
        if self.body is None:
            raise CouldNotParseKNXIP("No body defined in KNXIPFrame.")
        return self.header.to_knx() + self.body.to_knx()

    def __repr__(self) -> str:
        """Return object as readable string."""
        return f'<KNXIPFrame {self.header}\n body="{self.body}" />'

    def __eq__(self, other: object) -> bool:
        """Equal operator."""
        return self.__dict__ == other.__dict__
