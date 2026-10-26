#!/usr/bin/env python3
"""FLAPJAX holder audit — full Transfer-log replay, deploy block -> 2026-10-23 23:59:59 COT.

Token : 0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df (BEP-20, BSC, 18 decimals)
Target: block 129454096 == 2026-10-24T04:59:59Z == last second of 2026-10-23 in COT (UTC-5)
Range : 44582615 (deploy, 2024-12-04T16:11:12Z) .. 129454096

Writes:
  flapjax_transfers.json  — every Transfer log (block, tx, from, to, value)
  flapjax_holders.json    — balances at the target block, top list, conservation check
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = "0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df"
DEPLOY_BLOCK = 44_582_615
TARGET_BLOCK = 129_454_096
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000"
RPC = "https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3"
CHUNK = 50_000
WORKERS = 8
TXF = os.path.join(HERE, "flapjax_transfers.json")
OUT = os.path.join(HERE, "flapjax_holders.json")
LOGF = os.path.join(HERE, "flapjax_full.log")


def log(msg):
    line = time.strftime("%H:%M:%SZ", time.gmtime()) + " " + str(msg)
    print(line, flush=True)
    with open(LOGF, "a") as f:
        f.write(line + "\n")


def call(method, params, tries=10):
    delay = 1.5
    last = None
    for _ in range(tries):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        req = urllib.request.Request(RPC, data=body, headers={
            "content-type": "application/json", "user-agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            if "error" in d:
                raise RuntimeError(str(d["error"])[:120])
            return d["result"]
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(delay)
            delay = min(delay * 1.8, 30)
    raise RuntimeError(f"{method} failed: {last}")


def fetch_chunk(lo):
    hi = min(lo + CHUNK - 1, TARGET_BLOCK)
    logs = call("eth_getLogs", [{"address": TOKEN, "fromBlock": hex(lo),
                                 "toBlock": hex(hi), "topics": [TRANSFER]}])
    out = []
    for ev in logs or []:
        t = ev["topics"]
        if len(t) < 3:
            continue
        out.append({
            "block": int(ev["blockNumber"], 16),
            "tx": ev["transactionHash"],
            "from": "0x" + t[1][-40:],
            "to": "0x" + t[2][-40:],
            "value": int(ev["data"], 16) if ev["data"] not in ("0x", "") else 0,
        })
    return out


def main():
    starts = list(range(DEPLOY_BLOCK, TARGET_BLOCK + 1, CHUNK))
    log(f"scan {DEPLOY_BLOCK}..{TARGET_BLOCK} in {len(starts)} chunks of {CHUNK}, {WORKERS} workers")
    t0 = time.time()
    events = []
    done = 0
    with ThreadPoolExecutor(WORKERS) as ex:
        for res in ex.map(fetch_chunk, starts):
            events.extend(res)
            done += 1
            if done % 100 == 0:
                log(f"  {done}/{len(starts)} chunks, {len(events)} transfers, {time.time()-t0:.0f}s")
    events.sort(key=lambda e: (e["block"], e["tx"]))
    log(f"scan done: {len(events)} transfers in {time.time()-t0:.0f}s")
    json.dump(events, open(TXF, "w"))

    balances = defaultdict(int)
    for e in events:
        if e["value"] == 0:
            continue
        if e["from"] != ZERO:
            balances[e["from"]] -= e["value"]
        if e["to"] != ZERO:
            balances[e["to"]] += e["value"]
    negative = {a: v for a, v in balances.items() if v < 0}
    holders = sorted(((a, v) for a, v in balances.items() if v > 0), key=lambda x: -x[1])
    supply = int(call("eth_call", [{"to": TOKEN, "data": "0x18160ddd"}, hex(TARGET_BLOCK)]), 16)
    held = sum(v for _, v in holders)
    log(f"holders={len(holders)} supply={supply/1e18:.4f} sum={held/1e18:.4f} ok={held==supply} negative={len(negative)}")

    result = {
        "token": TOKEN,
        "symbol": "FLAPJAX",
        "decimals": 18,
        "chain": "BSC (56)",
        "target_block": TARGET_BLOCK,
        "target_block_ts": "2026-10-24T04:59:59Z",
        "target_local": "2026-10-23 23:59:59 COT (UTC-5)",
        "deploy_block": DEPLOY_BLOCK,
        "deploy_ts": "2024-12-04T16:11:12Z",
        "transfers": len(events),
        "total_supply": str(supply),
        "sum_of_balances": str(held),
        "supply_ok": held == supply,
        "negative_balances": negative,
        "holder_count": len(holders),
        "top": [{"address": a, "balance": str(v)} for a, v in holders[:60]],
    }
    json.dump(result, open(OUT, "w"), indent=1)
    log("wrote " + OUT)


if __name__ == "__main__":
    main()
