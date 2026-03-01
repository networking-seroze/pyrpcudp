"""Tests for RPCProtocol."""

from pyrpcudp import RPCProtocol


def test_protocol_instantiation():
    proto = RPCProtocol()
    assert proto.wait_timeout == 5.0
