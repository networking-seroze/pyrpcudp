<h1 align="center">pyrpcudp</h1>

<p align="center">
  <em>Lightweight asynchronous RPC over UDP for Python</em>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License"></a>
  <a href="https://pypi.org/project/pyrpcudp/"><img src="https://img.shields.io/badge/version-0.1.0-orange?style=flat-square" alt="Version"></a>
</p>

---

A minimal, async-first RPC framework built on top of Python's `asyncio.DatagramProtocol`. Define methods, call them remotely over UDP — that's it.

> Inspired by [bmuller/rpcudp](https://github.com/bmuller/rpcudp/tree/master) — a brilliant library that proved RPC over UDP is not only possible but practical for systems like [Kademlia](https://en.wikipedia.org/wiki/Kademlia) DHTs. **pyrpcudp** is a modern reimagining with native `async`/`await` support and zero-config simplicity.

## Why RPC over UDP?

RPC over UDP may sound unusual, but it's essential for:

- **Distributed Hash Tables** (Kademlia, Chord) where low-latency, connectionless messaging is critical
- **Service discovery** in local networks
- **Lightweight microservices** where TCP overhead is unnecessary
- **Real-time systems** that prioritize speed over guaranteed delivery

## Installation

```bash
pip install pyrpcudp
```

Or install from source:

```bash
git clone https://github.com/youruser/pyrpcudp.git
cd pyrpcudp
pip install -e ".[dev]"
```

## Quick Start

### 1. Define a Server

Subclass `RPCProtocol` and prefix your methods with `rpc_` to expose them:

```python
import asyncio
from pyrpcudp import RPCProtocol

class PingServer(RPCProtocol):
    def rpc_ping(self, name):
        return f"pong from {name}!"

    def rpc_add(self, a, b):
        return a + b

async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        PingServer, local_addr=("127.0.0.1", 9999)
    )
    print("Server listening on 127.0.0.1:9999")
    try:
        await asyncio.sleep(3600)
    finally:
        transport.close()

asyncio.run(main())
```

### 2. Call from a Client

Use the built-in `call()` method to invoke remote procedures:

```python
import asyncio
from pyrpcudp import RPCProtocol

class PingClient(RPCProtocol):
    async def ping(self, name):
        return await self.call(("127.0.0.1", 9999), "ping", name)

    async def add(self, a, b):
        return await self.call(("127.0.0.1", 9999), "add", a, b)

async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        PingClient, remote_addr=("127.0.0.1", 9999)
    )
    try:
        result = await protocol.ping("Alice")
        print(result)  # "pong from Alice!"

        total = await protocol.add(2, 3)
        print(total)  # 5
    except TimeoutError:
        print("Request timed out")
    finally:
        transport.close()

asyncio.run(main())
```

## How It Works

```
 Client                          Server
   |                               |
   |  --- JSON/UDP request --->    |
   |  {id, method, args, kwargs}   |
   |                               |  --> dispatch to rpc_<method>()
   |  <-- JSON/UDP response ---    |
   |  {id, result/error}           |
   |                               |
```

1. The client sends a JSON-encoded request with a unique message ID
2. The server looks up the `rpc_`-prefixed method, executes it, and sends back the result
3. The client matches the response to the pending request via the message ID
4. If no response arrives within the timeout window, a `TimeoutError` is raised

## API Reference

### `RPCProtocol(wait_timeout=5.0)`

Base class for both servers and clients.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `wait_timeout` | `float` | `5.0` | Seconds to wait for an RPC response before raising `TimeoutError` |

### `await protocol.call(addr, method, *args, **kwargs)`

Send an RPC request to a remote endpoint.

| Parameter | Type | Description |
|---|---|---|
| `addr` | `tuple[str, int]` | Target `(host, port)` |
| `method` | `str` | Remote method name (without the `rpc_` prefix) |
| `*args` | any | Positional arguments (must be JSON-serializable) |
| `**kwargs` | any | Keyword arguments (must be JSON-serializable) |

**Returns:** The return value from the remote method.

**Raises:** `TimeoutError` if no response is received within `wait_timeout` seconds.

### Defining RPC Methods

Any method on your `RPCProtocol` subclass that starts with `rpc_` is automatically available for remote calls:

```python
class MyService(RPCProtocol):
    def rpc_greet(self, name):          # called as "greet"
        return f"Hello, {name}!"

    def rpc_multiply(self, x, y):       # called as "multiply"
        return x * y
```

## Configuration

### Custom Timeout

```python
# Wait up to 10 seconds for responses
protocol = MyService(wait_timeout=10.0)
```

### Custom Endpoint Binding

```python
# Listen on all interfaces, port 5000
transport, protocol = await loop.create_datagram_endpoint(
    MyService, local_addr=("0.0.0.0", 5000)
)
```

## Project Structure

```
pyrpcudp/
  __init__.py       # Package exports
  protocol.py       # Core RPCProtocol implementation
examples/
  server.py         # Example server
  client.py         # Example client
tests/
  test_protocol.py  # Test suite
pyproject.toml      # Project configuration
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check pyrpcudp/
```

## Acknowledgements

This project is inspired by [**bmuller/rpcudp**](https://github.com/bmuller/rpcudp/tree/master), which pioneered the idea of RPC over UDP in Python for use in distributed hash table implementations. That project demonstrated that UDP-based RPC is a practical and elegant solution for systems like Kademlia. **pyrpcudp** builds on that spirit with a fresh, async-native implementation targeting modern Python (3.10+).

## License

MIT
