#!/usr/bin/env python3
"""Read-only proof of a SOL-paired Pump AMM creator-level fee claim.

A creator vault may aggregate multiple coins. This tool never attributes a claim
to a mint and never labels creator-level receipts as this project's revenue.
"""
import argparse
import json
import urllib.request

RPC = "https://api.mainnet-beta.solana.com"
PUMP_AMM = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
WSOL = "So11111111111111111111111111111111111111112"


def transaction(signature):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getTransaction",
                       "params": [signature, {"encoding": "jsonParsed",
                                              "maxSupportedTransactionVersion": 0}]}).encode()
    req = urllib.request.Request(RPC, body, {"Content-Type": "application/json",
                                             "User-Agent": "FEE100K-readonly-fee-audit/1.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(str(result["error"])[:250])
    return result.get("result")


def account_key(key):
    return key.get("pubkey") if isinstance(key, dict) else key


def audit(tx, creator, signature):
    out = {"signature": signature, "creator": creator,
           "classification": "UNVERIFIED", "mint_attribution": "UNKNOWN"}
    if not tx or (tx.get("meta") or {}).get("err") is not None:
        out["reason"] = "transaction unavailable or failed"
        return out
    msg = tx.get("transaction", {}).get("message", {})
    meta = tx.get("meta") or {}
    keys = msg.get("accountKeys") or []
    try:
        creator_index = [account_key(k) for k in keys].index(creator)
    except ValueError:
        out["reason"] = "creator not in account keys"
        return out
    outer = msg.get("instructions") or []
    if not any(i.get("programId") == PUMP_AMM for i in outer):
        out["reason"] = "Pump AMM program absent"
        return out
    if not any("Instruction: CollectCoinCreatorFee" in x
               for x in meta.get("logMessages") or []):
        out["reason"] = "creator fee collection log absent"
        return out
    # The creator's temporary wrapped-SOL account is closed to the creator.
    closed_to_creator = {
        i["parsed"].get("info", {}).get("account")
        for i in outer if isinstance(i.get("parsed"), dict)
        and i["parsed"].get("type") == "closeAccount"
        and i["parsed"].get("info", {}).get("destination") == creator
    }
    transfers = []
    for group in meta.get("innerInstructions") or []:
        for instruction in group.get("instructions") or []:
            parsed = instruction.get("parsed") or {}
            info = parsed.get("info") or {}
            amount = info.get("tokenAmount") or {}
            if (instruction.get("program") == "spl-token"
                    and parsed.get("type") == "transferChecked"
                    and info.get("mint") == WSOL
                    and info.get("destination") in closed_to_creator
                    and isinstance(amount.get("amount"), str)):
                transfers.append({"source_vault_token_account": info.get("source"),
                                  "amount_lamports": int(amount["amount"])})
    if len(transfers) != 1:
        out["reason"] = "expected exactly one vault-to-closed-WSOL transfer"
        return out
    pre = meta.get("preBalances") or []
    post = meta.get("postBalances") or []
    if creator_index >= len(pre) or creator_index >= len(post):
        out["reason"] = "missing creator balances"
        return out
    delta = post[creator_index] - pre[creator_index]
    amount = transfers[0]["amount_lamports"]
    fee = meta.get("fee")
    if delta <= 0 or not isinstance(fee, int) or amount - delta != fee:
        out["reason"] = "claim amount, wallet credit and fee do not reconcile"
        out.update({"amount_lamports": amount, "wallet_delta_lamports": delta, "tx_fee_lamports": fee})
        return out
    out.update({"classification": "VERIFIED_CREATOR_LEVEL_AMM_FEE_RECEIPT",
                "source_vault_token_account": transfers[0]["source_vault_token_account"],
                "amount_lamports": amount, "wallet_delta_lamports": delta,
                "tx_fee_lamports": fee, "quote_mint": WSOL,
                "source": "official Solana public RPC getTransaction"})
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--creator", required=True)
    parser.add_argument("--signature", action="append", required=True,
                        help="Bounded public transaction signature; may be repeated")
    args = parser.parse_args()
    if len(args.signature) > 10:
        parser.error("at most ten transactions per run")
    for signature in args.signature:
        print(json.dumps(audit(transaction(signature),
                              args.creator, signature), separators=(",", ":")))


if __name__ == "__main__":
    main()
