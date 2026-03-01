"""Example RPC UDP server."""

import asyncio

from pyrpcudp import RPCProtocol


class ExampleServer(RPCProtocol):
    def rpc_hello(self, name):
        print(f"Got hello from {name}")
        return f"Hello, {name}!"


async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        ExampleServer, local_addr=("127.0.0.1", 9999)
    )
    print("Server listening on 127.0.0.1:9999")
    try:
        await asyncio.sleep(3600)
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
