#!/usr/bin/env python3
"""
Shopify Admin API access-isolation test harness.

Purpose (authorized testing of YOUR OWN dev stores only):
  1. Confirm each store's token can read its own data (sanity check).
  2. Probe tenant isolation: use Store A's token against Store B's domain,
     and vice-versa. A correctly isolated platform must reject this.

Tokens are read from environment variables — never hardcoded, never committed.
Run:  python access_test.py        (after setting env vars, see .env.example)

This is read-only. It issues GET requests against the official Admin API.
It does NOT attempt to bypass auth, brute-force, or send high request volume.
"""
import os
import sys
import json
import urllib.request
import urllib.error

API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")

STORES = {
    "A": {
        "domain": os.environ.get("STORE_A_DOMAIN", ""),
        "token": os.environ.get("STORE_A_TOKEN", ""),
    },
    "B": {
        "domain": os.environ.get("STORE_B_DOMAIN", ""),
        "token": os.environ.get("STORE_B_TOKEN", ""),
    },
}

# Minimal read endpoints matching the requested read-only scopes.
ENDPOINTS = [
    ("shop",          "shop.json"),
    ("products",      "products.json?limit=1"),
    ("orders",        "orders.json?limit=1&status=any"),
    ("customers",     "customers.json?limit=1"),
    ("draft_orders",  "draft_orders.json?limit=1"),
]


def call(domain: str, token: str, path: str):
    """Return (status_code, short_body) for a GET against a store's Admin API."""
    url = f"https://{domain}/admin/api/{API_VERSION}/{path}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("X-Shopify-Access-Token", token)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(400).decode("utf-8", "replace")
            return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read(400).decode("utf-8", "replace")
        return e.code, body
    except Exception as e:  # noqa: BLE001
        return None, f"ERROR: {e}"


def require(name: str, store: dict):
    if not store["domain"] or not store["token"]:
        sys.exit(f"[config] Missing domain/token for store {name}. "
                 f"See .env.example and export the env vars first.")


def sanity_checks():
    print("== 1. Sanity: each token reads ITS OWN store ==")
    for name, s in STORES.items():
        require(name, s)
        status, _ = call(s["domain"], s["token"], "shop.json")
        verdict = "OK" if status == 200 else "UNEXPECTED"
        print(f"  Store {name} ({s['domain']}) -> shop.json : HTTP {status}  [{verdict}]")
    print()


def isolation_probe():
    print("== 2. Isolation: cross-tenant token use (MUST be rejected) ==")
    pairs = [("A", "B"), ("B", "A")]
    findings = []
    for tok_store, tgt_store in pairs:
        tok = STORES[tok_store]["token"]
        tgt = STORES[tgt_store]["domain"]
        print(f"  Using Store {tok_store}'s token against Store {tgt_store} ({tgt}):")
        for label, path in ENDPOINTS:
            status, body = call(tgt, tok, path)
            leaked = status == 200
            flag = "  <-- LEAK!" if leaked else ""
            print(f"    {label:<13} HTTP {status}{flag}")
            if leaked:
                findings.append((tok_store, tgt_store, label, body))
        print()
    return findings


def main():
    print(f"Shopify Admin API isolation test  (api {API_VERSION})\n")
    sanity_checks()
    findings = isolation_probe()
    print("== Result ==")
    if findings:
        print("  POTENTIAL ISOLATION FINDING(S) — cross-tenant read succeeded:")
        for tok_store, tgt_store, label, body in findings:
            print(f"   - Store {tok_store} token read {label} of Store {tgt_store}")
            print(f"     sample: {body[:200]}")
        print("\n  Capture full request/response and report via the program's policy.")
    else:
        print("  No cross-tenant access. Tenant isolation holds (expected for Shopify).")


if __name__ == "__main__":
    main()
