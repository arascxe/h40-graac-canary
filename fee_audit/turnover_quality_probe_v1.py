#!/usr/bin/env python3
"""Read-only, bounded turnover triage for a PumpSwap mint.

DEX Screener and GeckoTerminal are independent aggregators, not fee receipts.
This probe deliberately never labels volume organic or a creator's income.
"""
import argparse
import datetime as dt
import json
import urllib.request


def get_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "FEE100K-readonly-research/1.0"})
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.load(response)


def probe(mint):
    pairs = get_json("https://api.dexscreener.com/latest/dex/tokens/" + mint).get("pairs") or []
    candidates = [p for p in pairs if p.get("chainId") == "solana"
                 and p.get("dexId") == "pumpswap"
                 and p.get("baseToken", {}).get("address") == mint]
    if len(candidates) != 1:
        return {"mint": mint, "status": "PUMPSWAP_PAIR_AMBIGUOUS", "pool_count": len(candidates)}
    pair = candidates[0]
    pool = pair["pairAddress"]
    attr = get_json("https://api.geckoterminal.com/api/v2/networks/solana/pools/" + pool)["data"]["attributes"]
    created = dt.datetime.fromtimestamp(pair["pairCreatedAt"] / 1000, dt.timezone.utc).isoformat()
    tx = attr.get("transactions", {}).get("h24", {})
    volume = float(attr.get("volume_usd", {}).get("h24") or 0)
    liquidity = float(pair.get("liquidity", {}).get("usd") or 0)
    return {
        "mint": mint, "reported_pumpswap_pool": pool,
        "name": pair.get("baseToken", {}).get("name"),
        "pool_created_utc": created, "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "reported_h24_volume_usd": volume, "reported_h24_price_change_pct":
            attr.get("price_change_percentage", {}).get("h24"),
        "current_liquidity_usd": liquidity,
        "h24_volume_to_current_liquidity": round(volume / liquidity, 2) if liquidity else None,
        "h24_transactions": tx,
        "buyer_seller_unique_ratio": round(tx.get("buyers", 0) / tx["sellers"], 2)
            if tx.get("sellers") else None,
        "metadata_links_current_only": pair.get("info", {}).get("websites", [])
            + pair.get("info", {}).get("socials", []),
        "canonical_pool_and_owner_proof": "NOT_CHECKED",
        "mint_specific_fee_proof": "NOT_CHECKED",
        "creator_receipt_proof": "NOT_CHECKED",
        "maker_independence": "UNKNOWN_AGGREGATE_UNIQUE_COUNTS_ARE_NOT_SYBIL_PROOF",
        "premint_distribution": "UNKNOWN_CURRENT_LINKS_DO_NOT_PROVE_PREMINT_EXISTENCE",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mints", nargs="+", help="Solana token mint addresses")
    args = p.parse_args()
    if len(args.mints) > 4:
        p.error("At most four mints per bounded run")
    for mint in args.mints:
        try:
            print(json.dumps(probe(mint), ensure_ascii=False, separators=(",", ":")))
        except (KeyError, ValueError, OSError) as exc:
            print(json.dumps({"mint": mint, "status": "ACCESS_OR_DATA_FAILURE",
                              "error_type": type(exc).__name__}))


if __name__ == "__main__":
    main()
