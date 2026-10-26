# FLAPJAX holder audit — 2026-10-23 23:59:59 COT

**Token:** `FLAPJAX` (`0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df`, BEP-20, BSC, 18 decimals)  
**Snapshot block:** `129454096` — timestamp `2026-10-24T04:59:59Z`, i.e. the last second of 2026-10-23 in Colombia time (COT, UTC-5).  
**Total supply at that block:** `44,444,444,444` FLAPJAX (`totalSupply()` = `44,444,444,444,000,000,000,000,000,000` base units at the block)  
**Holders at that block:** 279 addresses with a non-zero balance  
**Transfers replayed:** 5,804 Transfer events, from the deployment block `44582615` to `129454096`

Balances below are not copied from an explorer. They are the running sum of every `Transfer` event emitted by the token between its deployment block and the snapshot block, which is then checked against `totalSupply()` at the same block: the sum of all 279 balances is `44,444,444,444` FLAPJAX, exactly equal to supply (check: `True`). Any missed or double-counted transfer would break that equality, so this is a complete replay, not a sample.

## Top 20 holders

| # | address | balance (FLAPJAX) | % of supply | type | label |
|---:|---|---:|---:|---|---|
| 1 | `0xca93ec685b8623688e6b236f9068034b298c2150` | 20,048,955,849.85 | 45.110% | contract | PancakeSwap V3 pool FLAPJAX/WBNB (1% fee tier) |
| 2 | `0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e` | 5,619,844,348.60 | 12.645% | contract | PancakeSwap V3 pool FLAPJAX/BTCB (1% fee tier) |
| 3 | `0x58fab046ce77064bf52c2eff4e163eb84386b8b4` | 2,334,009,348.88 | 5.252% | wallet | unlabelled |
| 4 | `0x000000000000000000000000000000000000dead` | 1,923,471,159.70 | 4.328% | wallet | burn address (0x…dEaD) |
| 5 | `0x2ea90ff709b0fb5decd1de944f644eecdc26d33a` | 1,175,621,343.20 | 2.645% | wallet | FLAPJAX deployer / contract creator |
| 6 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` | 848,761,365.01 | 1.910% | wallet | FlapJax treasury |
| 7 | `0x238a358808379702088667322f80ac48bad5e6c4` | 649,733,956.87 | 1.462% | contract | unlabelled |
| 8 | `0xf0e319587b54db351f4a20e2da09848fed4d8151` | 621,698,620.15 | 1.399% | wallet | unlabelled |
| 9 | `0x5dedb37eaa9145dd1a17d385d8c5e256871d6f16` | 611,866,236.48 | 1.377% | wallet | unlabelled |
| 10 | `0x9a937a531a3e4b7930a49548b64c4a3471d049e2` | 610,074,149.24 | 1.373% | wallet | unlabelled |
| 11 | `0xdbf2bdecf7dff212880552398b42e0ab997523a7` | 588,854,986.03 | 1.325% | wallet | unlabelled |
| 12 | `0x4492ca070a2caea1502fb807b389b62ab32eb0d3` | 586,603,504.42 | 1.320% | wallet | unlabelled |
| 13 | `0xc1fa91a815f59215aaefff20ea5c2f6718488d9a` | 559,775,724.99 | 1.260% | wallet | unlabelled |
| 14 | `0x7b6396e12928bee509473a2af01b30268343b7d5` | 525,463,217.00 | 1.182% | wallet | unlabelled |
| 15 | `0x4e1d0ab0c3730469c79c6746d222a28af81367ee` | 482,021,894.33 | 1.085% | wallet | unlabelled |
| 16 | `0x3a38d9c6a55f41286913b666501fb602bf0d05a2` | 482,000,000.00 | 1.085% | wallet | unlabelled |
| 17 | `0x5197681f65d2280d34866ee5a8c343bc67a71b20` | 482,000,000.00 | 1.085% | wallet | unlabelled |
| 18 | `0xe4ab694afb5499e6313e946c97d32e6c3fa5b754` | 444,444,445.01 | 1.000% | wallet | unlabelled |
| 19 | `0x74441dd9edc99fb5a66e7b35f139ce0e9fbd0954` | 407,298,532.69 | 0.916% | wallet | unlabelled |
| 20 | `0x639e263ce57bcee9866f01b1e6166fa20f965239` | 383,287,277.52 | 0.862% | wallet | unlabelled |

## Concentration

- top 5 hold **69.98%** of supply
- top 10 hold **77.50%** of supply
- top 20 hold **88.62%** of supply
- of the top 20, **3 are contracts** and **17 are ordinary wallets** (checked with `eth_getCode` at the snapshot block)

Read the pool rows carefully: a PancakeSwap pool holding 45% of supply is liquidity, not a person. Excluding the two pools, the burn address, the treasury and the deployer, the rest of the top 20 is a long tail of wallets and one unnamed contract between 0.86% and 5.25% — no single outside holder owns a blocking share.

How the supply got there, from the same replay: block `44582615` mints the whole 44.44B to `0x8d68e48bae…`, which forwards it in the same block to the launch contract `0x5c952063c7…`; that contract then distributes — 15.11B into the FLAPJAX/WBNB pool at block `44607858`, and the rest in tranches. Neither mint/launch contract appears in the table because neither has a material balance at the snapshot block: `0x8d68e48bae…` is at exactly 0 and `0x5c952063c7…` is left with 41,679 wei of dust.

## How each label was identified

| address | label | source |
|---|---|---|
| `0xca93ec685b8623688e6b236f9068034b298c2150` | PancakeSwap V3 pool FLAPJAX/WBNB (1% fee tier) | token0()/token1()/factory() on the address return FLAPJAX, WBNB and the PancakeSwap V3 factory 0x0bfbcf9f…1865; GoPlus Security API tags it `PancakeV3` |
| `0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e` | PancakeSwap V3 pool FLAPJAX/BTCB (1% fee tier) | token0()/token1()/factory() on the address return FLAPJAX, BTCB (0x7130d2a1…ad9c) and the same PancakeSwap V3 factory 0x0bfbcf9f…1865 |
| `0x000000000000000000000000000000000000dead` | burn address (0x…dEaD) | canonical burn address, no code, tokens provably unspendable |
| `0x2ea90ff709b0fb5decd1de944f644eecdc26d33a` | FLAPJAX deployer / contract creator | GoPlus Security API `creator_address` for the token; also the address in the contract-creation record |
| `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` | FlapJax treasury | named by the FlapJax team in the public task text (Receipt Relay Q46); no code at the target block |

Every other address in the top 20 is left **unlabelled on purpose**: nothing in public records ties it to a name, and a guess would be worse than a blank.

## Re-check any row

`balanceOf(address)` is an `eth_call` at the snapshot block. That needs a node that still keeps state at that height — the plain Binance dataseed nodes answer `missing trie node`, an archive-capable public endpoint does not:

```bash
# balance of the PancakeSwap V3 FLAPJAX/WBNB pool at the snapshot block
curl -s https://bsc-mainnet.public.blastapi.io -H 'content-type: application/json' -d '{
  "jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":"0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df",
  "data":"0x70a08231000000000000000000000000ca93ec685b8623688e6b236f9068034b298c2150"},
  "0x7b75010"]}'
# -> 0x40c81b8a6c6e4dec48c6dff3 = 20,048,955,849.85 FLAPJAX
```

`verify.py` re-reads all 20 balances from two independent public RPCs and prints PASS/FAIL per row.

Every top-20 balance was additionally read a second time from a **different RPC provider** and matched wei-for-wei: see `balance_second_rpc` / `second_rpc_agrees` in `holders.json` (20/20 agreed).

## Files

- `holders.json` — top 20 with labels, plus every holder at the snapshot block with balance and share
- `../flapjax_full.py` — the replay: `eth_getLogs` over the whole token history, 50k blocks per call
- `../flapjax_report.py` — classification (`eth_getCode`), second-RPC cross-check, table build

## Caveats

- A balance is a balance at one block; it says nothing about who controls the key. Contracts are marked because they have code, not because they are a team or a person.
- Token balances held by a pool are liquidity; the pool's own LP tokens sit with `0x25c9c4b56e820e0dea438b145284f02d9ca9bd52` (GoPlus SafeToken Locker), which holds no FLAPJAX.
- The treasury, the deployer and the burn address are named from public records (task text, GoPlus Security API, contract-creation record). Nothing else is inferred.

