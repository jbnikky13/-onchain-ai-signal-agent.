import re
import time
from typing import Any

import requests

from ..config import EVM_RPCS, REQUEST_TIMEOUT

RPCS = EVM_RPCS
_ADDRESS = re.compile(r"^0x[a-fA-F0-9]{40}$")
_TX = re.compile(r"^0x[a-fA-F0-9]{64}$")
_cache: dict[tuple[str, str, str], tuple[float, Any]] = {}


def _valid_address(address: str) -> str:
    if not _ADDRESS.fullmatch(address.strip()):
        raise ValueError("Invalid EVM address")
    return address.strip()


def _rpc(chain: str, method: str, params: list[Any], ttl: int = 15) -> Any:
    chain = chain.lower().strip()
    endpoint = RPCS.get(chain)
    if not endpoint:
        raise ValueError(f"Unsupported chain: {chain}")
    key = (chain, method, repr(params))
    now = time.time()
    if key in _cache and now - _cache[key][0] < ttl:
        return _cache[key][1]
    r = requests.post(endpoint, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    payload = r.json()
    if payload.get("error"):
        raise RuntimeError(payload["error"].get("message", "RPC request failed"))
    result = payload.get("result")
    _cache[key] = (now, result)
    return result


def _hex_int(value: str | None) -> int:
    return int(value or "0x0", 16)


def _native(value: str | None) -> float:
    return _hex_int(value) / 10**18


def _decode_string(raw: str | None) -> str | None:
    if not raw or raw == "0x":
        return None
    try:
        b = bytes.fromhex(raw[2:])
        if len(b) >= 64:
            offset = int.from_bytes(b[:32], "big")
            if offset + 32 <= len(b):
                n = int.from_bytes(b[offset:offset+32], "big")
                return b[offset+32:offset+32+n].decode(errors="replace")[:120]
        return b.rstrip(b"\x00").decode(errors="replace")[:120]
    except Exception:
        return None


def analyze_address(chain: str, address: str) -> dict[str, Any]:
    address = _valid_address(address)
    code, balance, nonce, block, gas = [
        _rpc(chain, method, params)
        for method, params in [
            ("eth_getCode", [address, "latest"]),
            ("eth_getBalance", [address, "latest"]),
            ("eth_getTransactionCount", [address, "latest"]),
            ("eth_blockNumber", []),
            ("eth_gasPrice", []),
        ]
    ]
    return {
        "ok": True, "chain": chain.lower(), "address": address,
        "type": "contract" if code not in (None, "0x") else "EOA",
        "native_balance": round(_native(balance), 8),
        "transaction_count": _hex_int(nonce), "latest_block": _hex_int(block),
        "gas_price_gwei": round(_native(gas) * 1000, 4),
        "contract_code_bytes": max(0, (len(code or "0x") - 2) // 2),
        "checked_at": time.time(),
    }


def contract_metadata(chain: str, address: str) -> dict[str, Any]:
    address = _valid_address(address)
    code = _rpc(chain, "eth_getCode", [address, "latest"], ttl=30)
    if code in (None, "0x"):
        return {"ok": False, "message": "No contract bytecode found at this address."}
    result: dict[str, Any] = {"ok": True, "chain": chain.lower(), "address": address}
    for key, selector in {"name":"06fdde03","symbol":"95d89b41","decimals":"313ce567","total_supply":"18160ddd"}.items():
        try:
            raw = _rpc(chain, "eth_call", [{"to": address, "data": "0x" + selector}, "latest"], ttl=60)
            result[key] = _hex_int(raw) if key in ("decimals", "total_supply") else _decode_string(raw)
        except Exception:
            result[key] = None
    result["bytecode_bytes"] = max(0, (len(code)-2)//2)
    result["proxy_hint"] = "363d3d373d3d3d363d73" in code.lower()
    return result


def transaction(chain: str, tx_hash: str) -> dict[str, Any]:
    if not _TX.fullmatch(tx_hash.strip()):
        raise ValueError("Invalid transaction hash")
    tx_hash = tx_hash.strip()
    tx = _rpc(chain, "eth_getTransactionByHash", [tx_hash], ttl=5)
    if not tx:
        return {"ok": False, "message": "Transaction not found on this chain."}
    receipt = _rpc(chain, "eth_getTransactionReceipt", [tx_hash], ttl=5)
    status = "pending" if not receipt else ("success" if receipt.get("status") == "0x1" else "failed")
    return {"ok": True, "chain": chain.lower(), "hash": tx_hash,
            "from": tx.get("from"), "to": tx.get("to"),
            "value_native": round(_native(tx.get("value")), 8),
            "block": _hex_int(tx.get("blockNumber")), "status": status,
            "gas_used": _hex_int(receipt.get("gasUsed")) if receipt else None}
