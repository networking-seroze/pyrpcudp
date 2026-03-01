"""Example RPC UDP client."""

import asyncio

from pyrpcudp import RPCProtocol


class ExampleClient(RPCProtocol):
    async def hello(self, name: str):
        return await self.call(("127.0.0.1", 9999), "hello", name)


async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        ExampleClient,
        remote_addr=("127.0.0.1", 9999),  # connect to server
    )

    try:
        # result = await protocol.call(("127.0.0.1", 9999), "hello", "Alice")
        result = await protocol.hello("Alice")
        print(f"Server replied: {result}")
    except TimeoutError as e:
        print(f"Request timed out: {e}")
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
