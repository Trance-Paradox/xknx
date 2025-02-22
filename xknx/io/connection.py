"""Manages a connection to the KNX bus."""
from __future__ import annotations

from enum import Enum, auto

from .const import DEFAULT_MCAST_PORT
from .gateway_scanner import GatewayScanFilter


class ConnectionType(Enum):
    """Enum class for different types of KNX/IP Connections."""

    AUTOMATIC = auto()
    ROUTING = auto()
    TUNNELING = auto()
    TUNNELING_TCP = auto()


class ConnectionConfig:
    """
    Connection configuration.

    Handles:
    * type of connection:
        * AUTOMATIC for using GatewayScanner for searching and finding KNX/IP devices in the network.
        * ROUTING use KNX/IP multicast routing.
        * TUNNELING connect to a specific KNX/IP tunneling device via UDP.
        * TUNNELING_TCP connect to a specific KNX/IP tunneling v2 device via TCP.
    * local_ip: Local ip of the interface though which KNXIPInterface should connect.
    * gateway_ip: IP of KNX/IP tunneling device.
    * gateway_port: Port of KNX/IP tunneling device.
    * route_back: For TUNNELING connection.
        The KNXnet/IP Server shall use the IP address and port in the received IP package
        as the target IP address or port number for the response to the KNXnet/IP Client.
    * auto_reconnect: Auto reconnect to KNX/IP tunneling device if connection cannot be established.
    * auto_reconnect_wait: Wait n seconds before trying to reconnect to KNX/IP tunneling device.
    * scan_filter: For AUTOMATIC connection, limit scan with the given filter
    """

    def __init__(
        self,
        connection_type: ConnectionType = ConnectionType.AUTOMATIC,
        local_ip: str | None = None,
        local_port: int = 0,
        gateway_ip: str | None = None,
        gateway_port: int = DEFAULT_MCAST_PORT,
        route_back: bool = False,
        auto_reconnect: bool = True,
        auto_reconnect_wait: int = 3,
        scan_filter: GatewayScanFilter = GatewayScanFilter(),
        threaded: bool = False,
    ):
        """Initialize ConnectionConfig class."""
        self.connection_type = connection_type
        self.local_ip = local_ip
        self.local_port = local_port
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port
        self.route_back = route_back
        self.auto_reconnect = auto_reconnect
        self.auto_reconnect_wait = auto_reconnect_wait
        self.scan_filter = scan_filter
        self.threaded = threaded

    def __eq__(self, other: object) -> bool:
        """Equality for ConnectionConfig class (used in unit tests)."""
        return self.__dict__ == other.__dict__
