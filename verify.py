#!/usr/bin/env python3
"""Re-check every top-20 balance in holders.json against two independent public BSC RPCs.

usage: python3 verify.py
exit code 0 = all rows agree with the published table
"""
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = "0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df"
BLOCK = 129_454_096
RPCS = [
    "https://bsc-mainnet.public.blastapi.io",
    "https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3",
]


def call(url, method, params, tries=8):
    delay = 1.5
    for _ in range(tries):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        req = urllib.request.Request(url, data=body, headers={
            "content-type": "application/json", "user-agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            if "error" in d:
                raise RuntimeError(str(d["error"])[:80])
            return d["result"]
        except Exception:  # noqa: BLE001
            time.sleep(delay)
            delay = min(delay * 1.7, 20)
    raise RuntimeError("rpc failed: " + url)


def balance(url, addr):
    data = "0x70a08231" + "0" * 24 + addr[2:].lower()
    return int(call(url, "eth_call", [{"to": TOKEN, "data": data}, hex(BLOCK)]), 16)


def main():
    d = json.load(open(os.path.join(HERE, "holders.json")))
    supply = int(d["total_supply"])
    bad = 0
    for r in d["top20"]:
        want = int(r["balance"])
        got = [balance(u, r["address"]) for u in RPCS]
        ok = all(g == want for g in got)
        bad += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} #{r['rank']:2} {r['address']} "
              f"{want / 1e18:>20,.2f} ({want / supply * 100:6.3f}%) "
              f"rpc1={got[0] / 1e18:,.2f} rpc2={got[1] / 1e18:,.2f}")
        time.sleep(0.3)
    print(f"\n{20 - bad}/20 rows verified on two independent RPCs")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
