"""Core RPC over UDP protocol implementation."""

import asyncio
import json
import uuid


class RPCProtocol(asyncio.DatagramProtocol):
    """Base class for RPC over UDP communication.

    Subclass this and define methods prefixed with ``rpc_`` to expose
    them as remote procedure calls.
    """

    def __init__(self, wait_timeout: float = 5.0):
        self.wait_timeout = wait_timeout
        self._pending: dict[str, asyncio.Future] = {}

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        # TODO: deserialize and dispatch RPC calls
        try:
            msg = json.loads(data)
        except (json.JSONDecodeError, UnicodeError):
            return

        msg_id = msg.get("id")
        msg_type = msg.get("type")

        if msg_type == "request":
            method_name = msg.get("method")
            args = msg.get("args", [])
            kwargs = msg.get("kwargs", {})

            method = getattr(self, f"rpc_{method_name}", None)
            if method is None:
                self._send_response(
                    addr, msg_id, error=f"Method '{method_name}' not found"
                )
                return

            try:
                result = method(*args, **kwargs)
                self._send_response(addr, msg_id, result=result)
            except Exception as e:
                self._send_response(addr, msg_id, error=str(e))

        elif msg_type == "response":
            # Response to one of our outgoing requests
            future = self._pending.pop(msg_id, None)
            if future and not future.done():
                error = msg.get("error")
                if error:
                    future.set_exception(Exception(error))
                else:
                    future.set_result(msg.get("result"))

    def _send_response(self, addr, msg_id, result=None, error=None):
        response = {"id": msg_id, "type": "response", "result": result, "error": error}
        self.transport.sendto(json.dumps(response).encode(), addr)

    async def call(self, addr: tuple[str, int], method: str, *args, **kwargs):
        """Send an RPC request and wait for the response"""
        msg_id = str(uuid.uuid4())
        message = {
            "id": msg_id,
            "type": "request",
            "method": method,
            "args": args,
            "kwargs": kwargs,
        }

        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self._pending[msg_id] = future
        self.transport.sendto(json.dumps(message).encode(), addr)

        try:
            return await asyncio.wait_for(future, timeout=self.wait_timeout)
        except asyncio.TimeoutError:
            self._pending.pop(msg_id, None)
            raise TimeoutError(f"RPC call '{method}' to {addr} timed out")

    def error_received(self, exc: Exception):
        print(f"Error received {exc}")

    def connection_lost(self, exc: Exception | None):
        if exc:
            print(f"Connection lost due to: {exc}")
