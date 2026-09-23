#!/usr/bin/env python3
"""Verify a single SOL-paired Pump AMM pool-to-creator-vault fee flow.

Requires independently established pool, mint, and creator-vault token account.
A verified transfer is fee accrual, not a wallet receipt or creator net profit.
"""
import argparse
import json
import urllib.request

RPC = "https://api.mainnet-beta.solana.com"
PUMP_AMM = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
WSOL = "So11111111111111111111111111111111111111112"


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = urllib.request.Request(RPC, body, {
        "Content-Type": "application/json", "User-Agent": "FEE100K-readonly-pool-audit/1.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        value = json.load(response)
    if "error" in value:
        raise RuntimeError(str(value["error"])[:250])
    return value.get("result")


def audit(tx, pool, mint, fee_vault_token, pool_owner):
    out = {"classification": "UNVERIFIED", "pool": pool, "mint": mint,
           "fee_vault_token_account": fee_vault_token,
           "claim_status": "NOT_CHECKED", "buyer_independence": "UNKNOWN"}
    if pool_owner != PUMP_AMM:
        out["reason"] = "pool is not owned by Pump AMM"
        return out
    if not tx or (tx.get("meta") or {}).get("err") is not None:
        out["reason"] = "transaction unavailable or failed"
        return out
    message = tx.get("transaction", {}).get("message", {})
    meta = tx.get("meta") or {}
    keys = [x.get("pubkey") if isinstance(x, dict) else x
            for x in message.get("accountKeys") or []]
    mints = {x.get("mint") for x in
             (meta.get("preTokenBalances") or []) + (meta.get("postTokenBalances") or [])}
    if pool not in keys or mint not in mints or fee_vault_token not in keys:
        out["reason"] = "pool, mint or vault absent in transaction"
        return out
    logs = meta.get("logMessages") or []
    if not any("Instruction: GetFeesWithQuoteMint" in x for x in logs):
        out["reason"] = "Pump AMM fee calculation log absent"
        return out
    transfers = []
    for group in meta.get("innerInstructions") or []:
        for instruction in group.get("instructions") or []:
            parsed = instruction.get("parsed") or {}
            info = parsed.get("info") or {}
            amount = info.get("tokenAmount") or {}
            if (instruction.get("program") == "spl-token"
                    and parsed.get("type") == "transferChecked"
                    and info.get("authority") == pool
                    and info.get("destination") == fee_vault_token
                    and info.get("mint") == WSOL
                    and isinstance(amount.get("amount"), str)):
                transfers.append(int(amount["amount"]))
    if len(transfers) != 1 or transfers[0] <= 0:
        out["reason"] = "one direct pool-to-vault WSOL transfer not found"
        return out
    out.update({"classification": "VERIFIED_MINT_POOL_CREATOR_VAULT_FLOW",
                "fee_amount_lamports": transfers[0],
                "quote_mint": WSOL,
                "block_time": tx.get("blockTime"),
                "source": "official Solana public RPC"})
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("signature", "pool", "mint", "fee-vault-token"):
        p.add_argument("--" + arg, required=True)
    a = p.parse_args()
    owner = (rpc("getAccountInfo", [a.pool, {"encoding": "base64"}]) or {}).get("value")
    tx = rpc("getTransaction", [a.signature, {
        "encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
    result = audit(tx, a.pool, a.mint, a.fee_vault_token, owner.get("owner") if owner else None)
    result["signature"] = a.signature
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
