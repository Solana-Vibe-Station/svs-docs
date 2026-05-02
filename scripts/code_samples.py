"""
Per-method code-sample generation for the SVS RPC OpenAPI specs.

Each method gets four code samples emitted as `x-codeSamples`:
  1. cURL — raw JSON-RPC POST to the public endpoint. Always first (default).
  2. Python — uses the `solana-py` SDK if a wrapper exists, else falls back to
     a raw HTTP call via `requests`.
  3. JavaScript — uses `@solana/web3.js` if a wrapper exists, else `fetch`.
  4. Rust — uses the `solana-client` crate if a wrapper exists, else `reqwest`.

The SDK_CALLS dict below holds, per method, an optional dict with `python`,
`javascript`, `rust` keys. When a key is present, the body for that language
is wrapped with the language's standard SDK boilerplate. When absent, the
raw JSON-RPC fallback is used for that language.

cURL is universal so it is generated unconditionally from `params_example`.

Usage:
    from code_samples import code_samples_for

    samples = code_samples_for(method_name="getBalance", params=["83ast..."])
    # samples is a list of dicts: [{lang, label, source}, ...]

The raw HTTP fallbacks are unconditionally correct because any JSON-RPC 2.0
endpoint accepts the standard envelope. Use that whenever the SDK wrapper
isn't worth its weight (custom params, niche method, complex pagination).
"""
from __future__ import annotations

import json
from typing import Any


PUBLIC_ENDPOINT = "https://public.rpc.solanavibestation.com"


# ---------------------------------------------------------------------------
# Method-specific SDK call bodies.
#
# Each value is a dict {language: snippet}. A snippet is the minimal core
# call expression — the wrappers below add imports, client construction,
# error handling, and printing.
#
# For methods not in this dict, all three SDK languages fall back to raw
# JSON-RPC over HTTP. cURL is always emitted from params_example.
# ---------------------------------------------------------------------------

SDK_CALLS: dict[str, dict[str, str]] = {

    # --- Account ---
    "getAccountInfo": {
        "python": (
            "pubkey = Pubkey.from_string(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")\n"
            "resp = client.get_account_info(pubkey, encoding=\"base64\")\n"
            "print(resp.value)"
        ),
        "javascript": (
            "const pubkey = new PublicKey(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\");\n"
            "const accountInfo = await connection.getAccountInfo(pubkey);\n"
            "console.log(accountInfo);"
        ),
        "rust": (
            "let pubkey = Pubkey::from_str(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")?;\n"
            "let account = client.get_account(&pubkey)?;\n"
            "println!(\"{:?}\", account);"
        ),
    },
    "getBalance": {
        "python": (
            "pubkey = Pubkey.from_string(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")\n"
            "resp = client.get_balance(pubkey)\n"
            "print(f\"{resp.value} lamports\")"
        ),
        "javascript": (
            "const pubkey = new PublicKey(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\");\n"
            "const lamports = await connection.getBalance(pubkey);\n"
            "console.log(`${lamports} lamports`);"
        ),
        "rust": (
            "let pubkey = Pubkey::from_str(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")?;\n"
            "let lamports = client.get_balance(&pubkey)?;\n"
            "println!(\"{} lamports\", lamports);"
        ),
    },
    "getMultipleAccounts": {
        "python": (
            "pubkeys = [\n"
            "    Pubkey.from_string(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\"),\n"
            "    Pubkey.from_string(\"11111111111111111111111111111111\"),\n"
            "]\n"
            "resp = client.get_multiple_accounts(pubkeys, encoding=\"base64\")\n"
            "for i, account in enumerate(resp.value):\n"
            "    print(f\"{pubkeys[i]}: {account}\")"
        ),
        "javascript": (
            "const pubkeys = [\n"
            "  new PublicKey(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\"),\n"
            "  new PublicKey(\"11111111111111111111111111111111\"),\n"
            "];\n"
            "const accounts = await connection.getMultipleAccountsInfo(pubkeys);\n"
            "console.log(accounts);"
        ),
        "rust": (
            "let pubkeys = [\n"
            "    Pubkey::from_str(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\")?,\n"
            "    Pubkey::from_str(\"11111111111111111111111111111111\")?,\n"
            "];\n"
            "let accounts = client.get_multiple_accounts(&pubkeys)?;\n"
            "println!(\"{:?}\", accounts);"
        ),
    },
    "getProgramAccounts": {
        "python": (
            "from solana.rpc.types import MemcmpOpts\n"
            "from solana.rpc.api import Client\n"
            "program_id = Pubkey.from_string(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")\n"
            "resp = client.get_program_accounts(program_id, encoding=\"base64\")\n"
            "print(f\"{len(resp.value)} accounts\")"
        ),
        "javascript": (
            "const programId = new PublicKey(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\");\n"
            "const accounts = await connection.getProgramAccounts(programId, {\n"
            "  filters: [{ dataSize: 165 }],\n"
            "});\n"
            "console.log(`${accounts.length} accounts`);"
        ),
        "rust": (
            "let program_id = Pubkey::from_str(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")?;\n"
            "let accounts = client.get_program_accounts(&program_id)?;\n"
            "println!(\"{} accounts\", accounts.len());"
        ),
    },
    "getTokenAccountBalance": {
        "python": (
            "token_account = Pubkey.from_string(\"7UVpfyV3PzWxNw3pcU88WGGgC4XSiTNVTPMK6P7vrqCi\")\n"
            "resp = client.get_token_account_balance(token_account)\n"
            "print(f\"{resp.value.ui_amount_string} ({resp.value.amount} raw)\")"
        ),
        "javascript": (
            "const tokenAccount = new PublicKey(\"7UVpfyV3PzWxNw3pcU88WGGgC4XSiTNVTPMK6P7vrqCi\");\n"
            "const balance = await connection.getTokenAccountBalance(tokenAccount);\n"
            "console.log(balance.value.uiAmountString);"
        ),
        "rust": (
            "let token_account = Pubkey::from_str(\"7UVpfyV3PzWxNw3pcU88WGGgC4XSiTNVTPMK6P7vrqCi\")?;\n"
            "let balance = client.get_token_account_balance(&token_account)?;\n"
            "println!(\"{}\", balance.ui_amount_string);"
        ),
    },
    "getTokenAccountsByOwner": {
        "python": (
            "from solana.rpc.types import TokenAccountOpts\n"
            "owner = Pubkey.from_string(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\")\n"
            "opts = TokenAccountOpts(program_id=Pubkey.from_string(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\"))\n"
            "resp = client.get_token_accounts_by_owner(owner, opts)\n"
            "print(f\"{len(resp.value)} token accounts\")"
        ),
        "javascript": (
            "const owner = new PublicKey(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\");\n"
            "const tokenProgram = new PublicKey(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\");\n"
            "const accounts = await connection.getTokenAccountsByOwner(owner, { programId: tokenProgram });\n"
            "console.log(`${accounts.value.length} token accounts`);"
        ),
        "rust": (
            "use solana_client::rpc_request::TokenAccountsFilter;\n"
            "let owner = Pubkey::from_str(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\")?;\n"
            "let token_program = Pubkey::from_str(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")?;\n"
            "let accounts = client.get_token_accounts_by_owner(&owner, TokenAccountsFilter::ProgramId(token_program))?;\n"
            "println!(\"{} token accounts\", accounts.len());"
        ),
    },
    "getTokenAccountsByDelegate": {
        "python": (
            "from solana.rpc.types import TokenAccountOpts\n"
            "delegate = Pubkey.from_string(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\")\n"
            "opts = TokenAccountOpts(program_id=Pubkey.from_string(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\"))\n"
            "resp = client.get_token_accounts_by_delegate(delegate, opts)\n"
            "print(f\"{len(resp.value)} delegated accounts\")"
        ),
        "javascript": (
            "const delegate = new PublicKey(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\");\n"
            "const tokenProgram = new PublicKey(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\");\n"
            "const accounts = await connection.getTokenAccountsByDelegate(delegate, { programId: tokenProgram });\n"
            "console.log(`${accounts.value.length} delegated accounts`);"
        ),
        "rust": (
            "use solana_client::rpc_request::TokenAccountsFilter;\n"
            "let delegate = Pubkey::from_str(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\")?;\n"
            "let token_program = Pubkey::from_str(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")?;\n"
            "let accounts = client.get_token_accounts_by_delegate(&delegate, TokenAccountsFilter::ProgramId(token_program))?;\n"
            "println!(\"{} delegated accounts\", accounts.len());"
        ),
    },
    "getTokenLargestAccounts": {
        "python": (
            "mint = Pubkey.from_string(\"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\")\n"
            "resp = client.get_token_largest_accounts(mint)\n"
            "for entry in resp.value[:5]:\n"
            "    print(f\"{entry.address}: {entry.ui_amount_string}\")"
        ),
        "javascript": (
            "const mint = new PublicKey(\"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\");\n"
            "const largest = await connection.getTokenLargestAccounts(mint);\n"
            "for (const entry of largest.value.slice(0, 5)) {\n"
            "  console.log(`${entry.address}: ${entry.uiAmountString}`);\n"
            "}"
        ),
        "rust": (
            "let mint = Pubkey::from_str(\"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\")?;\n"
            "let largest = client.get_token_largest_accounts(&mint)?;\n"
            "for entry in largest.iter().take(5) {\n"
            "    println!(\"{}: {}\", entry.address, entry.ui_amount_string);\n"
            "}"
        ),
    },
    "getTokenSupply": {
        "python": (
            "mint = Pubkey.from_string(\"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\")\n"
            "resp = client.get_token_supply(mint)\n"
            "print(f\"{resp.value.ui_amount_string} {mint}\")"
        ),
        "javascript": (
            "const mint = new PublicKey(\"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\");\n"
            "const supply = await connection.getTokenSupply(mint);\n"
            "console.log(supply.value.uiAmountString);"
        ),
        "rust": (
            "let mint = Pubkey::from_str(\"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\")?;\n"
            "let supply = client.get_token_supply(&mint)?;\n"
            "println!(\"{}\", supply.ui_amount_string);"
        ),
    },

    # --- Block ---
    "getBlock": {
        "python": (
            "resp = client.get_block(slot=416997240, max_supported_transaction_version=0)\n"
            "print(f\"blockhash={resp.value.blockhash} txs={len(resp.value.transactions or [])}\")"
        ),
        "javascript": (
            "const block = await connection.getBlock(416997240, { maxSupportedTransactionVersion: 0 });\n"
            "console.log(`blockhash=${block.blockhash} txs=${block.transactions.length}`);"
        ),
        "rust": (
            "use solana_transaction_status::UiTransactionEncoding;\n"
            "let block = client.get_block_with_encoding(416997240, UiTransactionEncoding::Json)?;\n"
            "println!(\"blockhash={} txs={}\", block.blockhash, block.transactions.len());"
        ),
    },
    "getBlockHeight": {
        "python": "print(client.get_block_height().value)",
        "javascript": "console.log(await connection.getBlockHeight());",
        "rust": "println!(\"{}\", client.get_block_height()?);",
    },
    "getBlocks": {
        "python": (
            "resp = client.get_blocks(start_slot=416997230, end_slot=416997240)\n"
            "print(resp.value)"
        ),
        "javascript": (
            "const blocks = await connection.getBlocks(416997230, 416997240);\n"
            "console.log(blocks);"
        ),
        "rust": (
            "let blocks = client.get_blocks(416997230, Some(416997240))?;\n"
            "println!(\"{:?}\", blocks);"
        ),
    },
    "getBlockTime": {
        "python": "print(client.get_block_time(416997240).value)",
        "javascript": "console.log(await connection.getBlockTime(416997240));",
        "rust": "println!(\"{}\", client.get_block_time(416997240)?);",
    },
    "getBlockCommitment": {
        "python": "print(client.get_block_commitment(416997240).value)",
        "javascript": (
            "// Not exposed by web3.js — use the raw RPC fallback shown in the cURL tab.\n"
            "const r = await fetch(\"https://public.rpc.solanavibestation.com\", {\n"
            "  method: \"POST\", headers: { \"Content-Type\": \"application/json\" },\n"
            "  body: JSON.stringify({ jsonrpc: \"2.0\", id: 1, method: \"getBlockCommitment\", params: [416997240] }),\n"
            "});\n"
            "console.log((await r.json()).result);"
        ),
        "rust": (
            "let commitment = client.get_block_commitment(416997240)?;\n"
            "println!(\"{:?}\", commitment);"
        ),
    },

    # --- Cluster ---
    "getClusterNodes": {
        "python": (
            "resp = client.get_cluster_nodes()\n"
            "print(f\"{len(resp.value)} nodes\")"
        ),
        "javascript": (
            "const nodes = await connection.getClusterNodes();\n"
            "console.log(`${nodes.length} nodes`);"
        ),
        "rust": (
            "let nodes = client.get_cluster_nodes()?;\n"
            "println!(\"{} nodes\", nodes.len());"
        ),
    },
    "getEpochInfo": {
        "python": "print(client.get_epoch_info().value)",
        "javascript": "console.log(await connection.getEpochInfo());",
        "rust": "println!(\"{:?}\", client.get_epoch_info()?);",
    },
    "getEpochSchedule": {
        "python": "print(client.get_epoch_schedule().value)",
        "javascript": "console.log(await connection.getEpochSchedule());",
        "rust": "println!(\"{:?}\", client.get_epoch_schedule()?);",
    },
    "getGenesisHash": {
        "python": "print(client.get_genesis_hash().value)",
        "javascript": "console.log(await connection.getGenesisHash());",
        "rust": "println!(\"{}\", client.get_genesis_hash()?);",
    },
    "getIdentity": {
        "python": "print(client.get_identity().value)",
        "javascript": (
            "// Not exposed by web3.js — use the raw RPC fallback.\n"
            "const r = await fetch(\"https://public.rpc.solanavibestation.com\", {\n"
            "  method: \"POST\", headers: { \"Content-Type\": \"application/json\" },\n"
            "  body: JSON.stringify({ jsonrpc: \"2.0\", id: 1, method: \"getIdentity\", params: [] }),\n"
            "});\n"
            "console.log((await r.json()).result);"
        ),
        "rust": "println!(\"{}\", client.get_identity()?);",
    },
    "getVersion": {
        "python": "print(client.get_version().value)",
        "javascript": "console.log(await connection.getVersion());",
        "rust": "println!(\"{:?}\", client.get_version()?);",
    },

    # --- Fees ---
    "getLatestBlockhash": {
        "python": (
            "resp = client.get_latest_blockhash()\n"
            "print(f\"blockhash={resp.value.blockhash} valid_until={resp.value.last_valid_block_height}\")"
        ),
        "javascript": (
            "const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash();\n"
            "console.log(`blockhash=${blockhash} valid_until=${lastValidBlockHeight}`);"
        ),
        "rust": (
            "let (blockhash, last_valid_block_height) = client.get_latest_blockhash_with_commitment(\n"
            "    solana_sdk::commitment_config::CommitmentConfig::finalized()\n"
            ")?;\n"
            "println!(\"blockhash={} valid_until={}\", blockhash, last_valid_block_height);"
        ),
    },
    "getMinimumBalanceForRentExemption": {
        "python": "print(client.get_minimum_balance_for_rent_exemption(165).value, \"lamports\")",
        "javascript": "console.log(await connection.getMinimumBalanceForRentExemption(165));",
        "rust": "println!(\"{} lamports\", client.get_minimum_balance_for_rent_exemption(165)?);",
    },
    "getFeeForMessage": {
        "python": (
            "# `message` is a base-64 encoded compiled Message (not a full Transaction).\n"
            "from solders.message import to_bytes_versioned\n"
            "import base64\n"
            "# msg_bytes = to_bytes_versioned(my_versioned_message)\n"
            "# encoded = base64.b64encode(msg_bytes).decode()\n"
            "encoded = \"AQABA0PJ8nGUKkR2lKZ8VcWQYWQzTGYYNCPdjhq2WaqLNUowVnPB6Q==\"\n"
            "resp = client.get_fee_for_message(encoded)\n"
            "print(resp.value, \"lamports\")"
        ),
        "javascript": (
            "// `message` is the compiled Message of your transaction.\n"
            "// const { value: fee } = await connection.getFeeForMessage(transaction.compileMessage());\n"
            "const encoded = \"AQABA0PJ8nGUKkR2lKZ8VcWQYWQzTGYYNCPdjhq2WaqLNUowVnPB6Q==\";\n"
            "const r = await fetch(\"https://public.rpc.solanavibestation.com\", {\n"
            "  method: \"POST\", headers: { \"Content-Type\": \"application/json\" },\n"
            "  body: JSON.stringify({ jsonrpc: \"2.0\", id: 1, method: \"getFeeForMessage\", params: [encoded] }),\n"
            "});\n"
            "console.log((await r.json()).result);"
        ),
        "rust": (
            "// In production, build a Message with solana_sdk::message::Message and call:\n"
            "//   client.get_fee_for_message(&my_message)?\n"
            "// Here we show the equivalent raw JSON-RPC call:\n"
            "let body = serde_json::json!({\n"
            "    \"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"getFeeForMessage\",\n"
            "    \"params\": [\"AQABA0PJ8nGUKkR2lKZ8VcWQYWQzTGYYNCPdjhq2WaqLNUowVnPB6Q==\"]\n"
            "});\n"
            "let resp: serde_json::Value = reqwest::blocking::Client::new()\n"
            "    .post(\"https://public.rpc.solanavibestation.com\").json(&body).send()?.json()?;\n"
            "println!(\"{}\", resp[\"result\"]);"
        ),
    },

    # --- Transactions ---
    "getSignaturesForAddress": {
        "python": (
            "address = Pubkey.from_string(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")\n"
            "resp = client.get_signatures_for_address(address, limit=10)\n"
            "for sig in resp.value:\n"
            "    print(sig.signature, sig.slot)"
        ),
        "javascript": (
            "const address = new PublicKey(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\");\n"
            "const sigs = await connection.getSignaturesForAddress(address, { limit: 10 });\n"
            "for (const s of sigs) console.log(s.signature, s.slot);"
        ),
        "rust": (
            "use solana_client::rpc_client::GetConfirmedSignaturesForAddress2Config;\n"
            "let address = Pubkey::from_str(\"TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq\")?;\n"
            "let cfg = GetConfirmedSignaturesForAddress2Config { limit: Some(10), ..Default::default() };\n"
            "let sigs = client.get_signatures_for_address_with_config(&address, cfg)?;\n"
            "for s in &sigs { println!(\"{} {}\", s.signature, s.slot); }"
        ),
    },
    "getSignatureStatuses": {
        "python": (
            "from solders.signature import Signature\n"
            "sigs = [Signature.from_string(\"4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa\")]\n"
            "resp = client.get_signature_statuses(sigs, search_transaction_history=True)\n"
            "print(resp.value)"
        ),
        "javascript": (
            "const sigs = [\"4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa\"];\n"
            "const statuses = await connection.getSignatureStatuses(sigs, { searchTransactionHistory: true });\n"
            "console.log(statuses.value);"
        ),
        "rust": (
            "use solana_sdk::signature::Signature;\n"
            "let sigs = [Signature::from_str(\"4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa\")?];\n"
            "let statuses = client.get_signature_statuses_with_history(&sigs)?;\n"
            "println!(\"{:?}\", statuses.value);"
        ),
    },
    "getTransaction": {
        "python": (
            "from solders.signature import Signature\n"
            "sig = Signature.from_string(\"4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa\")\n"
            "resp = client.get_transaction(sig, max_supported_transaction_version=0)\n"
            "print(resp.value)"
        ),
        "javascript": (
            "const sig = \"4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa\";\n"
            "const tx = await connection.getTransaction(sig, { maxSupportedTransactionVersion: 0 });\n"
            "console.log(tx);"
        ),
        "rust": (
            "use solana_sdk::signature::Signature;\n"
            "use solana_transaction_status::UiTransactionEncoding;\n"
            "let sig = Signature::from_str(\"4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa\")?;\n"
            "let tx = client.get_transaction(&sig, UiTransactionEncoding::Json)?;\n"
            "println!(\"{:?}\", tx);"
        ),
    },
    "getTransactionCount": {
        "python": "print(client.get_transaction_count().value)",
        "javascript": "console.log(await connection.getTransactionCount());",
        "rust": "println!(\"{}\", client.get_transaction_count()?);",
    },
    "sendTransaction": {
        "python": (
            "# Build and sign the transaction first; here we send pre-encoded bytes.\n"
            "# In real usage:  resp = client.send_transaction(my_signed_tx)\n"
            "#                 print(resp.value)\n"
            "# The example below uses send_raw_transaction with already-signed bytes.\n"
            "from solana.rpc.types import TxOpts\n"
            "raw_tx_bytes = bytes.fromhex(\"00\")  # replace with your signed tx bytes\n"
            "resp = client.send_raw_transaction(raw_tx_bytes, opts=TxOpts(skip_preflight=False, preflight_commitment=\"processed\"))\n"
            "print(resp.value)"
        ),
        "javascript": (
            "// Build and sign the transaction with your keypair first; here\n"
            "// we send pre-serialized bytes.\n"
            "// const sig = await connection.sendTransaction(signedTx, { skipPreflight: false, preflightCommitment: \"processed\" });\n"
            "const rawTx = Buffer.from(\"00\", \"hex\");  // replace with your signed tx bytes\n"
            "const sig = await connection.sendRawTransaction(rawTx, {\n"
            "  skipPreflight: false,\n"
            "  preflightCommitment: \"processed\",\n"
            "});\n"
            "console.log(sig);"
        ),
        "rust": (
            "use solana_sdk::transaction::Transaction;\n"
            "use solana_client::rpc_config::RpcSendTransactionConfig;\n"
            "// Build & sign your `Transaction` first, then:\n"
            "// let sig = client.send_transaction_with_config(&tx, RpcSendTransactionConfig {\n"
            "//     skip_preflight: false,\n"
            "//     preflight_commitment: Some(CommitmentLevel::Processed),\n"
            "//     ..Default::default()\n"
            "// })?;\n"
            "// println!(\"{}\", sig);\n"
            "println!(\"requires a built+signed Transaction — see the docs above\");"
        ),
    },
    "simulateTransaction": {
        "python": (
            "# Build the transaction first; here we show the call shape.\n"
            "from solana.rpc.types import TxOpts\n"
            "from solders.transaction import VersionedTransaction\n"
            "# resp = client.simulate_transaction(my_versioned_tx, sig_verify=False, replace_recent_blockhash=True)\n"
            "# print(resp.value.logs)\n"
            "print(\"Build a VersionedTransaction first, then call client.simulate_transaction(tx)\")"
        ),
        "javascript": (
            "// Build a VersionedTransaction first.\n"
            "// const sim = await connection.simulateTransaction(versionedTx, { sigVerify: false, replaceRecentBlockhash: true });\n"
            "// console.log(sim.value.logs);\n"
            "console.log(\"Build a VersionedTransaction first, then call connection.simulateTransaction(tx)\");"
        ),
        "rust": (
            "use solana_client::rpc_config::RpcSimulateTransactionConfig;\n"
            "// let sim = client.simulate_transaction_with_config(&tx, RpcSimulateTransactionConfig {\n"
            "//     sig_verify: false, replace_recent_blockhash: true, ..Default::default()\n"
            "// })?;\n"
            "// println!(\"{:?}\", sim.value.logs);\n"
            "println!(\"Build & sign a Transaction first, then simulate_transaction_with_config\");"
        ),
    },

    # --- Slots ---
    "getSlot": {
        "python": "print(client.get_slot().value)",
        "javascript": "console.log(await connection.getSlot());",
        "rust": "println!(\"{}\", client.get_slot()?);",
    },
    "getSlotLeader": {
        "python": "print(client.get_slot_leader().value)",
        "javascript": "console.log(await connection.getSlotLeader());",
        "rust": "println!(\"{}\", client.get_slot_leader()?);",
    },
    "getSlotLeaders": {
        "python": (
            "resp = client.get_slot_leaders(start_slot=416997230, limit=10)\n"
            "print(resp.value)"
        ),
        "javascript": (
            "const leaders = await connection.getSlotLeaders(416997230, 10);\n"
            "console.log(leaders);"
        ),
        "rust": (
            "let leaders = client.get_slot_leaders(416997230, 10)?;\n"
            "println!(\"{:?}\", leaders);"
        ),
    },
    "getLeaderSchedule": {
        "python": (
            "resp = client.get_leader_schedule()\n"
            "print(f\"{len(resp.value or {})} leaders\")"
        ),
        "javascript": (
            "const schedule = await connection.getLeaderSchedule();\n"
            "console.log(`${Object.keys(schedule || {}).length} leaders`);"
        ),
        "rust": (
            "let schedule = client.get_leader_schedule(None)?;\n"
            "println!(\"{} leaders\", schedule.map(|s| s.len()).unwrap_or(0));"
        ),
    },

    # --- Validators / Inflation / Supply ---
    "getVoteAccounts": {
        "python": (
            "resp = client.get_vote_accounts()\n"
            "print(f\"current={len(resp.current)} delinquent={len(resp.delinquent)}\")"
        ),
        "javascript": (
            "const va = await connection.getVoteAccounts();\n"
            "console.log(`current=${va.current.length} delinquent=${va.delinquent.length}`);"
        ),
        "rust": (
            "let va = client.get_vote_accounts()?;\n"
            "println!(\"current={} delinquent={}\", va.current.len(), va.delinquent.len());"
        ),
    },
    "getInflationGovernor": {
        "python": "print(client.get_inflation_governor().value)",
        "javascript": "console.log(await connection.getInflationGovernor());",
        "rust": "println!(\"{:?}\", client.get_inflation_governor()?);",
    },
    "getInflationRate": {
        "python": "print(client.get_inflation_rate().value)",
        "javascript": "console.log(await connection.getInflationRate());",
        "rust": "println!(\"{:?}\", client.get_inflation_rate()?);",
    },
    "getInflationReward": {
        "python": (
            "addrs = [Pubkey.from_string(\"FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR\")]\n"
            "resp = client.get_inflation_reward(addrs, epoch=964)\n"
            "print(resp.value)"
        ),
        "javascript": (
            "const addrs = [new PublicKey(\"FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR\")];\n"
            "const rewards = await connection.getInflationReward(addrs, 964);\n"
            "console.log(rewards);"
        ),
        "rust": (
            "let addrs = [Pubkey::from_str(\"FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR\")?];\n"
            "let rewards = client.get_inflation_reward(&addrs, Some(964))?;\n"
            "println!(\"{:?}\", rewards);"
        ),
    },
    "getSupply": {
        "python": "print(client.get_supply().value)",
        "javascript": "console.log((await connection.getSupply()).value);",
        "rust": "println!(\"{:?}\", client.supply()?.value);",
    },
    "getLargestAccounts": {
        "python": "print(client.get_largest_accounts().value[:5])",
        "javascript": (
            "const largest = await connection.getLargestAccounts({ filter: \"circulating\" });\n"
            "console.log(largest.value.slice(0, 5));"
        ),
        "rust": (
            "let resp = client.get_largest_accounts_with_config(\n"
            "    solana_client::rpc_config::RpcLargestAccountsConfig { commitment: None, filter: None }\n"
            ")?;\n"
            "for entry in resp.value.iter().take(5) {\n"
            "    println!(\"{}: {}\", entry.address, entry.lamports);\n"
            "}"
        ),
    },

    # --- Misc ---
    "requestAirdrop": {
        "python": (
            "from solana.rpc.api import Client\n"
            "# Airdrops only succeed on devnet/testnet:\n"
            "devnet = Client(\"https://api.devnet.solana.com\")\n"
            "pubkey = Pubkey.from_string(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\")\n"
            "resp = devnet.request_airdrop(pubkey, 1_000_000_000)\n"
            "print(resp.value)"
        ),
        "javascript": (
            "const devnet = new Connection(\"https://api.devnet.solana.com\");\n"
            "const pubkey = new PublicKey(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\");\n"
            "const sig = await devnet.requestAirdrop(pubkey, 1_000_000_000);\n"
            "console.log(sig);"
        ),
        "rust": (
            "let devnet = RpcClient::new(\"https://api.devnet.solana.com\".to_string());\n"
            "let pubkey = Pubkey::from_str(\"83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri\")?;\n"
            "let sig = devnet.request_airdrop(&pubkey, 1_000_000_000)?;\n"
            "println!(\"{}\", sig);"
        ),
    },
    "minimumLedgerSlot": {
        "python": "print(client.get_minimum_ledger_slot().value)",
        "javascript": (
            "// Not exposed by web3.js — use the raw RPC fallback shown in the cURL tab.\n"
            "const r = await fetch(\"https://public.rpc.solanavibestation.com\", {\n"
            "  method: \"POST\", headers: { \"Content-Type\": \"application/json\" },\n"
            "  body: JSON.stringify({ jsonrpc: \"2.0\", id: 1, method: \"minimumLedgerSlot\", params: [] }),\n"
            "});\n"
            "console.log((await r.json()).result);"
        ),
        "rust": "println!(\"{}\", client.minimum_ledger_slot()?);",
    },
    "getRecentPerformanceSamples": {
        "python": (
            "resp = client.get_recent_performance_samples(limit=5)\n"
            "for s in resp.value:\n"
            "    print(s)"
        ),
        "javascript": (
            "const samples = await connection.getRecentPerformanceSamples(5);\n"
            "for (const s of samples) console.log(s);"
        ),
        "rust": (
            "let samples = client.get_recent_performance_samples(Some(5))?;\n"
            "for s in &samples { println!(\"{:?}\", s); }"
        ),
    },
    "getRecentPrioritizationFees": {
        "python": (
            "# solana-py doesn't expose this yet; use the underlying provider.\n"
            "import requests\n"
            "r = requests.post(\"https://public.rpc.solanavibestation.com\", json={\n"
            "    \"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"getRecentPrioritizationFees\", \"params\": [[]]\n"
            "}).json()\n"
            "for s in r[\"result\"][:5]:\n"
            "    print(s)"
        ),
        "javascript": (
            "const fees = await connection.getRecentPrioritizationFees();\n"
            "for (const s of fees.slice(0, 5)) console.log(s);"
        ),
        "rust": (
            "let fees = client.get_recent_prioritization_fees(&[])?;\n"
            "for s in fees.iter().take(5) { println!(\"{:?}\", s); }"
        ),
    },

    # --- Health / blockhash validity / stake ---
    "getHealth": {
        "python": (
            "# Not exposed by solana-py — use the underlying HTTP transport.\n"
            "import requests\n"
            "r = requests.post(\"https://public.rpc.solanavibestation.com\", json={\n"
            "    \"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"getHealth\", \"params\": []\n"
            "}).json()\n"
            "print(r[\"result\"])  # \"ok\" if healthy"
        ),
        "javascript": (
            "// Not exposed by web3.js — use the raw RPC fallback.\n"
            "const r = await fetch(\"https://public.rpc.solanavibestation.com\", {\n"
            "  method: \"POST\", headers: { \"Content-Type\": \"application/json\" },\n"
            "  body: JSON.stringify({ jsonrpc: \"2.0\", id: 1, method: \"getHealth\", params: [] }),\n"
            "});\n"
            "console.log((await r.json()).result);  // \"ok\" if healthy"
        ),
        "rust": "println!(\"{}\", client.get_health().map(|_| \"ok\").unwrap_or(\"unhealthy\"));",
    },
    "isBlockhashValid": {
        "python": (
            "# Not exposed by solana-py — use the underlying HTTP transport.\n"
            "import requests\n"
            "r = requests.post(\"https://public.rpc.solanavibestation.com\", json={\n"
            "    \"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"isBlockhashValid\",\n"
            "    \"params\": [\"3Eq21vXNB5s86c62bVuUfTeaMif1N2kUqRPBmGRJhyTA\", {\"commitment\": \"processed\"}]\n"
            "}).json()\n"
            "print(r[\"result\"])"
        ),
        "javascript": (
            "const blockhash = \"3Eq21vXNB5s86c62bVuUfTeaMif1N2kUqRPBmGRJhyTA\";\n"
            "const valid = await connection.isBlockhashValid(blockhash, { commitment: \"processed\" });\n"
            "console.log(valid);"
        ),
        "rust": (
            "use solana_sdk::hash::Hash;\n"
            "use solana_sdk::commitment_config::CommitmentConfig;\n"
            "let blockhash = Hash::from_str(\"3Eq21vXNB5s86c62bVuUfTeaMif1N2kUqRPBmGRJhyTA\")?;\n"
            "let valid = client.is_blockhash_valid(&blockhash, CommitmentConfig::processed())?;\n"
            "println!(\"{}\", valid);"
        ),
    },
    "getStakeMinimumDelegation": {
        "python": (
            "# Not exposed by solana-py — use the underlying HTTP transport.\n"
            "import requests\n"
            "r = requests.post(\"https://public.rpc.solanavibestation.com\", json={\n"
            "    \"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"getStakeMinimumDelegation\", \"params\": []\n"
            "}).json()\n"
            "print(r[\"result\"][\"value\"], \"lamports\")"
        ),
        "javascript": (
            "// web3.js does not expose this method directly. Raw RPC fallback:\n"
            "const r = await fetch(\"https://public.rpc.solanavibestation.com\", {\n"
            "  method: \"POST\", headers: { \"Content-Type\": \"application/json\" },\n"
            "  body: JSON.stringify({ jsonrpc: \"2.0\", id: 1, method: \"getStakeMinimumDelegation\", params: [] }),\n"
            "});\n"
            "console.log((await r.json()).result.value, \"lamports\");"
        ),
        "rust": (
            "println!(\"{} lamports\", client.get_stake_minimum_delegation()?);"
        ),
    },

    # --- Block-related extras without web3.js wrappers ---
    "getBlocksWithLimit": {
        "python": (
            "# solana-py doesn't expose this directly; use the raw transport.\n"
            "import requests\n"
            "r = requests.post(\"https://public.rpc.solanavibestation.com\", json={\n"
            "    \"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"getBlocksWithLimit\",\n"
            "    \"params\": [416997230, 10]\n"
            "}).json()\n"
            "print(r[\"result\"])"
        ),
        "javascript": (
            "const blocks = await connection.getBlocksWithLimit(416997230, 10);\n"
            "console.log(blocks);"
        ),
        "rust": (
            "let blocks = client.get_blocks_with_limit(416997230, 10)?;\n"
            "println!(\"{:?}\", blocks);"
        ),
    },
    "getBlockProduction": {
        "python": (
            "import requests\n"
            "r = requests.post(\"https://public.rpc.solanavibestation.com\", json={\n"
            "    \"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"getBlockProduction\", \"params\": []\n"
            "}).json()\n"
            "print(r[\"result\"])"
        ),
        "javascript": (
            "// web3.js does not expose this method. Raw RPC fallback:\n"
            "const r = await fetch(\"https://public.rpc.solanavibestation.com\", {\n"
            "  method: \"POST\", headers: { \"Content-Type\": \"application/json\" },\n"
            "  body: JSON.stringify({ jsonrpc: \"2.0\", id: 1, method: \"getBlockProduction\", params: [] }),\n"
            "});\n"
            "console.log((await r.json()).result);"
        ),
        "rust": (
            "let production = client.get_block_production()?;\n"
            "println!(\"{:?}\", production.value);"
        ),
    },
}


# ---------------------------------------------------------------------------
# Boilerplate wrappers per language.
# ---------------------------------------------------------------------------

PY_HEADER = (
    "from solana.rpc.api import Client\n"
    "from solders.pubkey import Pubkey\n"
    "\n"
    f"client = Client(\"{PUBLIC_ENDPOINT}\")\n"
    "\n"
)

JS_HEADER = (
    "import { Connection, PublicKey } from \"@solana/web3.js\";\n"
    "\n"
    f"const connection = new Connection(\"{PUBLIC_ENDPOINT}\", \"confirmed\");\n"
    "\n"
)

RS_HEADER = (
    "use solana_client::rpc_client::RpcClient;\n"
    "use solana_sdk::pubkey::Pubkey;\n"
    "use std::str::FromStr;\n"
    "\n"
    f"let client = RpcClient::new(\"{PUBLIC_ENDPOINT}\".to_string());\n"
    "\n"
)


def _curl_sample(method: str, params: list[Any]) -> str:
    """Generate a cURL command that POSTs the JSON-RPC call to the public endpoint."""
    body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    encoded = json.dumps(body, separators=(",", ":"))
    # Use single-quote JSON for shell safety; escape any single quotes inside.
    encoded_for_shell = encoded.replace("'", "'\\''")
    return (
        f"curl -X POST {PUBLIC_ENDPOINT} \\\n"
        "  -H \"Content-Type: application/json\" \\\n"
        f"  -d '{encoded_for_shell}'"
    )


def _python_raw(method: str, params: list[Any]) -> str:
    return (
        "import requests\n"
        "\n"
        f"resp = requests.post(\"{PUBLIC_ENDPOINT}\", json={{\n"
        "    \"jsonrpc\": \"2.0\", \"id\": 1,\n"
        f"    \"method\": \"{method}\",\n"
        f"    \"params\": {json.dumps(params)}\n"
        "}).json()\n"
        "print(resp[\"result\"])"
    )


def _javascript_raw(method: str, params: list[Any]) -> str:
    return (
        f"const resp = await fetch(\"{PUBLIC_ENDPOINT}\", {{\n"
        "  method: \"POST\",\n"
        "  headers: { \"Content-Type\": \"application/json\" },\n"
        "  body: JSON.stringify({\n"
        "    jsonrpc: \"2.0\", id: 1,\n"
        f"    method: \"{method}\",\n"
        f"    params: {json.dumps(params)}\n"
        "  }),\n"
        "});\n"
        "const data = await resp.json();\n"
        "console.log(data.result);"
    )


def _rust_raw(method: str, params: list[Any]) -> str:
    return (
        "use serde_json::json;\n"
        "\n"
        f"let body = json!({{\n"
        "    \"jsonrpc\": \"2.0\", \"id\": 1,\n"
        f"    \"method\": \"{method}\",\n"
        f"    \"params\": {json.dumps(params)}\n"
        "}});\n"
        f"let resp: serde_json::Value = reqwest::blocking::Client::new()\n"
        f"    .post(\"{PUBLIC_ENDPOINT}\").json(&body).send()?.json()?;\n"
        "println!(\"{}\", resp[\"result\"]);"
    )


def code_samples_for(method: str, params: list[Any]) -> list[dict[str, str]]:
    """Return the four-language `x-codeSamples` block for a given method.

    The first entry is always cURL (default tab in GitBook). The Python /
    JavaScript / Rust entries use the SDK wrappers from `SDK_CALLS` if a
    body is registered, otherwise fall back to a raw HTTP call.
    """
    sdk = SDK_CALLS.get(method, {})

    py_body = sdk.get("python")
    if py_body:
        py = PY_HEADER + py_body
    else:
        py = _python_raw(method, params)

    js_body = sdk.get("javascript")
    if js_body:
        js = JS_HEADER + js_body
    else:
        js = _javascript_raw(method, params)

    rs_body = sdk.get("rust")
    if rs_body:
        rs = RS_HEADER + rs_body
    else:
        rs = _rust_raw(method, params)

    return [
        {"lang": "shell",      "label": "cURL",       "source": _curl_sample(method, params)},
        {"lang": "python",     "label": "Python",     "source": py},
        {"lang": "javascript", "label": "JavaScript", "source": js},
        {"lang": "rust",       "label": "Rust",       "source": rs},
    ]


# ---------------------------------------------------------------------------
# Multi-example catalog: optional named examples beyond the default.
# Each entry is a list of {name, summary, params} dicts.
# Cap at 2 extra examples per method so total <= 3 examples (default + 2).
# ---------------------------------------------------------------------------

EXTRA_EXAMPLES: dict[str, list[dict[str, Any]]] = {
    "getAccountInfo": [
        {
            "name": "json_parsed",
            "summary": "Use jsonParsed to get program-aware decoding (e.g. SPL token accounts).",
            "params": ["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"encoding": "jsonParsed", "commitment": "finalized"}],
        },
        {
            "name": "with_data_slice",
            "summary": "Fetch only the first 64 bytes of the account's data field.",
            "params": ["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"encoding": "base64", "dataSlice": {"offset": 0, "length": 64}}],
        },
    ],
    "getBalance": [
        {
            "name": "with_commitment",
            "summary": "Specify a commitment level explicitly.",
            "params": ["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"commitment": "confirmed"}],
        },
        {
            "name": "with_min_context_slot",
            "summary": "Require the node's root to be at or above a specific slot before responding.",
            "params": ["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {"commitment": "confirmed", "minContextSlot": 416990000}],
        },
    ],
    "getMultipleAccounts": [
        {
            "name": "json_parsed",
            "summary": "Decode known program account layouts (SPL token, stake, etc.) with jsonParsed.",
            "params": [["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", "11111111111111111111111111111111"], {"encoding": "jsonParsed"}],
        },
    ],
    "getProgramAccounts": [
        {
            "name": "with_filters",
            "summary": "Filter by data size + memcmp on the SPL Token program (mint authority offset).",
            "params": ["TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq", {
                "encoding": "base64",
                "filters": [{"dataSize": 165}, {"memcmp": {"offset": 0, "bytes": "3Mc6vR", "encoding": "base58"}}],
            }],
        },
        {
            "name": "with_context",
            "summary": "Wrap the response in a `{context, value}` envelope so you get the slot back too.",
            "params": ["TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq", {"encoding": "base64", "withContext": True}],
        },
    ],
    "getBlock": [
        {
            "name": "signatures_only",
            "summary": "Fetch a block but only return signatures, not full transactions. Much smaller payload.",
            "params": [416997240, {"transactionDetails": "signatures", "rewards": False, "maxSupportedTransactionVersion": 0}],
        },
        {
            "name": "with_rewards",
            "summary": "Include block-level rewards (stake/voting payouts) in the response.",
            "params": [416997240, {"rewards": True, "maxSupportedTransactionVersion": 0}],
        },
    ],
    "getBlocks": [
        {
            "name": "open_ended",
            "summary": "Pass only `startSlot`; the node returns up to ~500k subsequent confirmed blocks.",
            "params": [416997230],
        },
    ],
    "getSignaturesForAddress": [
        {
            "name": "page_back",
            "summary": "Paginate backwards by passing the last signature you've seen as `before`.",
            "params": ["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", {
                "limit": 1000,
                "before": "4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa",
            }],
        },
    ],
    "getSignatureStatuses": [
        {
            "name": "with_history",
            "summary": "Search the long-term ledger archive in addition to recent slots.",
            "params": [["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa"], {"searchTransactionHistory": True}],
        },
    ],
    "sendTransaction": [
        {
            "name": "skip_preflight",
            "summary": "Skip preflight simulation when you trust the transaction (saves latency).",
            "params": ["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", {"skipPreflight": True}],
        },
    ],
    "simulateTransaction": [
        {
            "name": "with_account_state",
            "summary": "Return post-simulation state for specific accounts.",
            "params": ["4hXTCkRzt9WyecNzV1XPgCDfGAZzQKNxLXgynz5QDuWWPSAZBZSHptvWRL3BjCvzUXRdKvHL2b7yGrRQcWyaqsa", {
                "sigVerify": False,
                "replaceRecentBlockhash": True,
                "accounts": {"addresses": ["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri"], "encoding": "base64"},
            }],
        },
    ],
    "getLatestBlockhash": [
        {
            "name": "processed",
            "summary": "Get the very latest blockhash regardless of confirmation. Useful pre-tx-build.",
            "params": [{"commitment": "processed"}],
        },
    ],
    "getRecentPrioritizationFees": [
        {
            "name": "for_specific_accounts",
            "summary": "Scope to recent blocks that referenced the given accounts.",
            "params": [["83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri", "TokenkegQfeZyiNwAJsyFbPVwwQnLjMi6tsmbMrWcbq"]],
        },
    ],
    "getSupply": [
        {
            "name": "exclude_account_list",
            "summary": "Skip the (potentially long) list of non-circulating accounts in the response.",
            "params": [{"commitment": "finalized", "excludeNonCirculatingAccountsList": True}],
        },
    ],
    "getLargestAccounts": [
        {
            "name": "non_circulating",
            "summary": "Return only the largest non-circulating accounts.",
            "params": [{"filter": "nonCirculating"}],
        },
    ],
    "getVoteAccounts": [
        {
            "name": "single_validator",
            "summary": "Filter to a single validator's vote account.",
            "params": [{"votePubkey": "FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR"}],
        },
    ],
    "getInflationReward": [
        {
            "name": "without_epoch",
            "summary": "Omit the epoch to get the most recent finalized epoch's rewards.",
            "params": [["FbXMxhgoCYbZ4dWaCVzJWeFqW2tQ8sR82Hi8YyQrEaxR"]],
        },
    ],
}


# Historical RPC: same shape as Solana RPC (just different paths). Reuse SDK_CALLS
# where the method semantics are identical, plus add /historical-specific notes.
HISTORICAL_NOTE_PYTHON = (
    "# The historical archive is served from a separate path on every SVS\n"
    "# server. The solana-py Client must be pointed at the /historical URL:\n"
)
HISTORICAL_NOTE_JS = (
    "// The historical archive is served from a separate path on every SVS\n"
    "// server. Construct a Connection pointed at the /historical URL:\n"
)
HISTORICAL_NOTE_RUST = (
    "// The historical archive is served from a separate path on every SVS\n"
    "// server. Build the RpcClient with the /historical URL:\n"
)


def _historical_curl(method: str, params: list[Any]) -> str:
    body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    encoded = json.dumps(body, separators=(",", ":"))
    encoded_for_shell = encoded.replace("'", "'\\''")
    return (
        f"curl -X POST {PUBLIC_ENDPOINT}/historical \\\n"
        "  -H \"Content-Type: application/json\" \\\n"
        f"  -d '{encoded_for_shell}'"
    )


def historical_code_samples_for(method: str, params: list[Any]) -> list[dict[str, str]]:
    """Same as code_samples_for but for the /historical path."""
    sdk = SDK_CALLS.get(method, {})  # historical uses same method names

    py_header = (
        "from solana.rpc.api import Client\n"
        "from solders.pubkey import Pubkey\n"
        "\n"
        + HISTORICAL_NOTE_PYTHON
        + f"client = Client(\"{PUBLIC_ENDPOINT}/historical\")\n\n"
    )
    js_header = (
        "import { Connection, PublicKey } from \"@solana/web3.js\";\n"
        "\n"
        + HISTORICAL_NOTE_JS
        + f"const connection = new Connection(\"{PUBLIC_ENDPOINT}/historical\", \"confirmed\");\n\n"
    )
    rs_header = (
        "use solana_client::rpc_client::RpcClient;\n"
        "use solana_sdk::pubkey::Pubkey;\n"
        "use std::str::FromStr;\n"
        "\n"
        + HISTORICAL_NOTE_RUST
        + f"let client = RpcClient::new(\"{PUBLIC_ENDPOINT}/historical\".to_string());\n\n"
    )

    py = (py_header + sdk["python"]) if sdk.get("python") else _python_raw(method, params).replace(
        PUBLIC_ENDPOINT, f"{PUBLIC_ENDPOINT}/historical"
    )
    js = (js_header + sdk["javascript"]) if sdk.get("javascript") else _javascript_raw(method, params).replace(
        PUBLIC_ENDPOINT, f"{PUBLIC_ENDPOINT}/historical"
    )
    rs = (rs_header + sdk["rust"]) if sdk.get("rust") else _rust_raw(method, params).replace(
        PUBLIC_ENDPOINT, f"{PUBLIC_ENDPOINT}/historical"
    )

    return [
        {"lang": "shell",      "label": "cURL",       "source": _historical_curl(method, params)},
        {"lang": "python",     "label": "Python",     "source": py},
        {"lang": "javascript", "label": "JavaScript", "source": js},
        {"lang": "rust",       "label": "Rust",       "source": rs},
    ]
