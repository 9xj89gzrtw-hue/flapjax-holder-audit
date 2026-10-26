#!/usr/bin/env python3
"""Rebuild audit/holders.json with EVERY holder (not just the top 60).

flapjax_full.py only persists the top 60 in flapjax_holders.json to keep that file
small; the full balance map is fully recoverable from flapjax_transfers.json, so we
replay it again here (no RPC needed) and keep the labels/top20 already produced by
flapjax_report.py.
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audit")
ZERO = "0x0000000000000000000000000000000000000000"


def main():
    holders = json.load(open(os.path.join(HERE, "flapjax_holders.json")))
    out = json.load(open(os.path.join(AUD, "holders.json")))
    transfers = json.load(open(os.path.join(HERE, "flapjax_transfers.json")))

    balances = defaultdict(int)
    for e in transfers:
        if e["value"] == 0:
            continue
        if e["from"] != ZERO:
            balances[e["from"]] -= e["value"]
        if e["to"] != ZERO:
            balances[e["to"]] += e["value"]

    supply = int(holders["total_supply"])
    full = sorted(((a, v) for a, v in balances.items() if v > 0), key=lambda x: -x[1])
    assert sum(v for _, v in full) == supply, "conservation broke on re-replay"
    assert len(full) == holders["holder_count"], (len(full), holders["holder_count"])

    out["all_holders"] = [
        {"address": a, "balance": str(v), "share_pct": round(v / supply * 100, 6)}
        for a, v in full
    ]
    out["all_holders_note"] = (
        f"All {len(full)} addresses with a non-zero balance at block {holders['target_block']}, "
        "ranked. Derived by replaying every Transfer log; sum equals totalSupply exactly."
    )
    out["pool_checks"] = {
        "0xca93ec685b8623688e6b236f9068034b298c2150": {
            "token0": "0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df",
            "token1": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
            "factory": "0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865",
            "fee": 10000,
            "read_at_block": holders["target_block"],
        },
        "0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e": {
            "token0": "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c",
            "token1": "0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df",
            "factory": "0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865",
            "fee": 10000,
            "read_at_block": holders["target_block"],
        },
    }
    json.dump(out, open(os.path.join(AUD, "holders.json"), "w"), indent=1)
    print(f"wrote {len(full)} holders, supply conserved")


if __name__ == "__main__":
    main()
