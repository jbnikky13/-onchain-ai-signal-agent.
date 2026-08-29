import re
import time
from typing import Any

import requests

from ..config import REQUEST_TIMEOUT

RPCS = {
    "ethereum": "https://cloudflare-eth.com",
    "base": "https://mainnet.base.org",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "optimism": "https://mainnet.optimism.io",
    "polygon": "https://polygon-rpc.com",
    "bnb": "https://bsc-dataseed.binance.org",
}

_ADDRESS = re.compile(r"^0x[a-fA-F0-9]{40}$")
_TX = re.compile(r"^0x[a-fA-F0-9]{64}$")
_cache: dict[tuple[str, str, tuple[Any, ...]], tuple[float, Any]] = {}


def _valid_address(address: str) -> str:
    if not _ADDRESS.match(address):
        raise ValueError("Invalid EVM address")
    return address


def _rpc(chain: str, method: str, params: list[Any], ttl: int = 15) -> Any:
    chain = chain.lower()
    if chain not in RPCS:
        raise ValueError(f"Unsupported chain: {chain}")
    key = (chain, method, tuple(params))
    now = time.time()
    cached = _cache.get(key)
    if cached and now - cached[0] < ttl:
        return cached[1]
    response = requests.post(
        RPCS[chain],
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload["error"].get("message", "RPC request failed"))
    result = payload.get("result")
    _cache[key] = (now, result)
    return result


def _wei_to_native(value: str | None) -> float:
    return int(value or "0x0", 16) / 10**18


def _hex_int(value: str | None) -> int:
    return int(value or "0x0", 16)


def analyze_address(chain: str, address: str) -> dict[str, Any]:
    address = _valid_address(address)
    chain = chain.lower()
    balance = _rpc(chain, "eth_getBalance", [address, "latest"])
    code = _rpc(chain, "eth_getCode", [address, "latest"])
    nonce = _rpc(chain, "eth_getTransactionCount", [address, "latest"])
    block = _rpc(chain, "eth_blockNumber", [])
    gas = _rpc(chain, "eth_gasPrice", [])
    is_contract = code not in (None, "0x", "0x0")
    return {
        "ok": True,
        "chain": chain,
        "address": address,
        "type": "contract" if is_contract else "EOA",
        "native_balance": round(_wei_to_native(balance), 8),
        "transaction_count": _hex_int(nonce),
        "latest_block": _hex_int(block),
        "gas_price_gwei": round(_wei_to_native(gas) * 1000, 4),
        "contract_code_bytes": max(0, (len(code or "0x") - 2) // 2),
        "rpc": RPCS[chain],
        "checked_at": time.time(),
    }


def transaction(chain: str, tx_hash: str) -> dict[str, Any]:
    if not _TX.match(tx_hash):
        raise ValueError("Invalid transaction hash")
    tx = _rpc(chain, "eth_getTransactionByHash", [tx_hash], ttl=5)
    if not tx:
        return {"ok": False, "message": "Transaction not found on this chain."}
    receipt = _rpc(chain, "eth_getTransactionReceipt", [tx_hash], ttl=5)
    return {
        "ok": True,
        "chain": chain.lower(),
        "hash": tx_hash,
        "from": tx.get("from"),
        "to": tx.get("to"),
        "value_native": round(_wei_to_native(tx.get("value")), 8),
        "block": _hex_int(tx.get("blockNumber")),
        "status": "success" if receipt and receipt.get("status") == "0x1" else "failed" if receipt else "pending",
        "gas_used": _hex_int(receipt.get("gasUsed")) if receipt else None,
    }


def contract_metadata(chain: str, address: str) -> dict[str, Any]:
    address = _valid_address(address)
    code = _rpc(chain, "eth_getCode", [address, "latest"], ttl=30)
    if code in (None, "0x", "0x0"):
        return {"ok": False, "message": "No contract bytecode found at this address."}

    calls = {
        "name": "0x06fdde03",
        "symbol": "0x95d89b41",
        "decimals": "0x313ce567",
        "total_supply": "0x18160ddd",
    }
    result: dict[str, Any] = {"ok": True, "chain": chain.lower(), "address": address}
    for key, data in calls.items():
        try:
            raw = _rpc(chain, "eth_call", [{"to": address, "data": data}, "latest"], ttl=30)
            if key == "decimals":
                result[key] = _hex_int(raw)
            elif key == "total_supply":
                result[key] = _hex_int(raw)
            else:
                result[key] = _decode_abi_string(raw)
        except Exception:
            result[key] = None
    result["bytecode_bytes"] = max(0, (len(code) - 2) // 2)
    result["proxy_hint"] = "363d3d373d3d3d363d73" in code.lower()
    return result


def _decode_abi_string(raw: str | None) -> str | None:
    if not raw or raw == "0x":
        return None
    try:
        data = bytes.fromhex(raw[2:])
        if len(data) >= 96:
            offset = int.from_bytes(data[:32], "big")
            if offset + 32 <= len(data):
                length = int.from_bytes(data[offset:offset + 32], "big")
                start = offset + 32
                return data[start:start + length].decode("utf-8", errors="replace")[:120]
        return data.rstrip(b"\x00").decode("utf-8", errors="replace")[:120]
    except Exception:
        return None
