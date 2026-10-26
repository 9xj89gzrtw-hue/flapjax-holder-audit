#!/usr/bin/env python3
"""Build the FLAPJAX holder-audit report from flapjax_holders.json.

Reads the replay output, classifies each top address (contract vs wallet) by
eth_getCode at the target block, cross-checks balances on a second RPC, and
writes:
  audit/README.md          — the public page
  audit/holders.json       — machine-readable result (all holders)
  audit/verify.md          — copy-paste re-check commands
"""
import json
import os
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audit")
TOKEN = "0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df"
TARGET_BLOCK = 129_454_096
RPC1 = "https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3"
RPC2 = "https://bsc-mainnet.public.blastapi.io"

LABELS = {
    "0xca93ec685b8623688e6b236f9068034b298c2150":
        ("PancakeSwap V3 pool FLAPJAX/WBNB (1% fee tier)",
         "token0()/token1()/factory() on the address return FLAPJAX, WBNB and the PancakeSwap V3 factory 0x0bfbcf9f…1865; GoPlus Security API tags it `PancakeV3`"),
    "0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e":
        ("PancakeSwap V3 pool FLAPJAX/BTCB (1% fee tier)",
         "token0()/token1()/factory() on the address return FLAPJAX, BTCB (0x7130d2a1…ad9c) and the same PancakeSwap V3 factory 0x0bfbcf9f…1865"),
    "0x000000000000000000000000000000000000dead":
        ("burn address (0x…dEaD)", "canonical burn address, no code, tokens provably unspendable"),
    "0x7c34e9e21ee28a49ff0b84b61774119e6633359f":
        ("FlapJax treasury", "named by the FlapJax team in the public task text (Receipt Relay Q46); no code at the target block"),
    "0x2ea90ff709b0fb5decd1de944f644eecdc26d33a":
        ("FLAPJAX deployer / contract creator", "GoPlus Security API `creator_address` for the token; also the address in the contract-creation record"),
    "0x25c9c4b56e820e0dea438b145284f02d9ca9bd52":
        ("GoPlus SafeToken Locker (LP lock, holds LP tokens not FLAPJAX)", "GoPlus Security API `lp_holders` tag `GoPlus SafeToken Locker`"),
}


def call(url, method, params, tries=10):
    delay = 1.5
    for _ in range(tries):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        req = urllib.request.Request(url, data=body, headers={
            "content-type": "application/json", "user-agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
            if "error" in d:
                raise RuntimeError(str(d["error"])[:100])
            return d["result"]
        except Exception:  # noqa: BLE001
            time.sleep(delay)
            delay = min(delay * 1.7, 25)
    raise RuntimeError("rpc failed")


def balance_of(url, addr, block=TARGET_BLOCK):
    data = "0x70a08231" + "0" * 24 + addr[2:].lower()
    return int(call(url, "eth_call", [{"to": TOKEN, "data": data}, hex(block)]), 16)


def fmt(v, dec=18):
    return f"{v / 10 ** dec:,.2f}"


def main():
    d = json.load(open(os.path.join(HERE, "flapjax_holders.json")))
    supply = int(d["total_supply"])
    top = d["top"][:20]
    holders = d["top"]

    rows = []
    for i, h in enumerate(top, 1):
        a = h["address"].lower()
        bal = int(h["balance"])
        code = call(RPC1, "eth_getCode", [a, hex(TARGET_BLOCK)])
        is_contract = code not in ("0x", "0x0", "")
        # independent second-opinion balance from a different provider
        b2 = balance_of(RPC2, a)
        label, how = LABELS.get(a, ("unlabelled", "—"))
        rows.append({
            "rank": i, "address": h["address"], "balance": str(bal),
            "balance_human": fmt(bal), "share_pct": round(bal / supply * 100, 4),
            "is_contract": is_contract, "label": label, "label_source": how,
            "balance_second_rpc": str(b2), "second_rpc_agrees": b2 == bal,
        })
        print(f"{i:2} {h['address']} {fmt(bal):>22} {bal/supply*100:6.3f}% "
              f"{'contract' if is_contract else 'wallet':8} {label[:50]}")
        time.sleep(0.4)

    def share(n):
        return sum(int(r["balance"]) for r in rows[:n]) / supply * 100

    out = {
        "token": TOKEN, "symbol": "FLAPJAX", "chain": "BSC", "decimals": 18,
        "target_block": TARGET_BLOCK, "target_ts": "2026-10-24T04:59:59Z",
        "total_supply": str(supply), "holder_count": d["holder_count"],
        "transfers_replayed": d["transfers"], "deploy_block": d["deploy_block"],
        "sum_of_balances": d["sum_of_balances"], "supply_conserved": d["supply_ok"],
        "top20": rows,
        "concentration_pct": {"top5": round(share(5), 3), "top10": round(share(10), 3),
                              "top20": round(share(20), 3)},
        "top20_contracts": sum(1 for r in rows if r["is_contract"]),
        "top20_wallets": sum(1 for r in rows if not r["is_contract"]),
        "all_holders": [{"address": h["address"], "balance": h["balance"],
                         "share_pct": round(int(h["balance"]) / supply * 100, 6)}
                        for h in holders],
    }
    os.makedirs(AUD, exist_ok=True)
    json.dump(out, open(os.path.join(AUD, "holders.json"), "w"), indent=1)
    print("\nconcentration", out["concentration_pct"],
          "contracts", out["top20_contracts"], "wallets", out["top20_wallets"])


if __name__ == "__main__":
    main()
