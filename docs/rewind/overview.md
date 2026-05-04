# Rewind

Rewind is Solana Vibe Station's historical state and simulation service. It answers questions that the standard Solana RPC can't — what an account looked like at a past slot, how an account changed across a slot range, what a transaction would have done if it had run earlier, and where on chain a particular pattern actually occurred.

Reads run synchronously over JSON-RPC. Long-running batch simulations run as async jobs that you submit, poll, and paginate.

## What you can do with Rewind

- **Look up historical account state.** `getAccountInfo` and `getMultipleAccounts` return account data at any slot inside the archive window — or anchored immediately before / after a known transaction, so you don't have to know the slot in advance.
- **Walk an account's change history.** `getAccountChanges` returns paginated, newest-first per-write history for one pubkey across a slot range, with optional data hydration. `getAccountDiff` gives a two-point structural diff between any two positions.
- **Replay transactions against historical state.** `simulateHistoricalTransaction` runs a fully-signed `VersionedTransaction` through the SVM against the archive's exact state at a chosen slot — same feature set, sysvars, address-lookup tables, and program bytecode that the network had at that moment.
- **Run batch simulations across slot ranges.** Submit a sweep, a trigger-driven scan, or a discovery job; poll for completion; paginate the results. Useful for backtesting, opportunity research, and post-mortems.
- **Inspect coverage.** `getRewindCoverage` reports the slot range Rewind currently has, plus a list of any gaps inside that range. Critical for audit and trust.

## Endpoint

Rewind is served on the same tier hostnames as standard RPC. Choose a tier and POST JSON-RPC 2.0 to the root path:

```
https://{tier}.rpc.solanavibestation.com
```

Replace `{tier}` with one of: `public`, `basic`, `ultra`, `elite`, `epic`. Authentication is the standard SVS scheme — `Authorization: <api-key>` header or `?api_key=<api-key>` query parameter.

## Methods

| Method | Purpose |
|---|---|
| [`getAccountInfo`](./getaccountinfo.md) | Point-in-time historical account lookup. |
| [`getMultipleAccounts`](./getmultipleaccounts.md) | Batched lookup at one shared historical position. |
| [`getAccountChanges`](./getaccountchanges.md) | Paginated per-write change history for one pubkey. |
| [`getAccountDiff`](./getaccountdiff.md) | Two-point structural diff for one pubkey. |
| [`getRewindCoverage`](./getrewindcoverage.md) | Archive-wide coverage and gap list. |
| [`simulateHistoricalTransaction`](./simulatehistoricaltransaction.md) | Replay a transaction against archive state at a chosen position. |

## Positioning a query

Rewind's read methods and the simulator share one positioning vocabulary. Every endpoint that needs a historical position accepts one of:

- **End-of-slot** — set `slot: N` to position at the latest version of the account at or before slot N.
- **Per-transaction anchored** — set `anchor: { signature, position }` to position immediately before (`"before"`) or immediately after (`"after"`) a known transaction. The slot is resolved from the signature, so you don't have to know it. Useful for "what state did this tx see?" / "what did it leave behind?" workflows.

There is no "latest" mode — one of `slot` or `anchor` is always required. The actual slot the response was served from is echoed back in `value.rewindSlot`, which may be earlier than the queried slot if the account didn't change in the queried slot. That field is also a stable cache key.

`getAccountDiff` accepts both modes independently per side via `slotA` / `anchorA` and `slotB` / `anchorB`. `getAccountChanges` uses `[fromSlot, toSlot]` for the range and an opaque `before` cursor (returned as `value.next` on the previous page) for pagination.

## Archive coverage

Rewind keeps a rolling window of recent history. Anything older than the window is no longer queryable; query `getRewindCoverage` to see the current `earliestSlot` and `latestSlot`.

The coverage response also lists any **gaps** — slot ranges where ingest is incomplete. There are two kinds:

- **Missing.** Real archive holes. Reads and simulations that resolve into a missing range refuse with `-32018 SlotInArchiveGap` instead of silently serving stale at-or-before data. Pass `tolerateGaps: true` if you explicitly want the older, possibly-stale answer. `getAccountChanges` doesn't refuse on missing ranges; it surfaces them inline via `value.gaps[]` so walkers can see discontinuities in their stream.
- **Skipped.** Leader-skipped slots that produced no block on chain. These are not archive failures, so they don't appear as gaps and don't trigger refusal — the at-or-before answer is genuinely correct.

## Filtered accounts

To keep the archive efficient, Rewind drops writes for a small set of high-volume, low-query-value account classes (Vote and Stake accounts by default). Read endpoints behave normally for these accounts but reflect state-at-snapshot rather than the latest write. **Simulations that touch a filtered account refuse with `-32017 FilteredAccountStale`** to avoid silently producing diverged results.

The active filter set is reported on `getRewindCoverage` under `filteredOwners` and `filteredPubkeys`. Typical workloads — DeFi swaps, arbitrage analysis, liquidations, NFT marketplace flows — never touch the filtered classes.

## Error codes

All Rewind errors come back via the standard JSON-RPC `error` envelope. The Rewind-specific codes are:

| Code | Meaning |
|---|---|
| `-32014` | Slot not available — the queried slot is past the archive's `latestSlot`. Route to live RPC. |
| `-32015` | Slot before earliest — the queried slot is older than the archive window. |
| `-32016` | Signature not found — the `anchor.signature` isn't indexed (the tx didn't land in an ingested slot, or it produced no archived writes). |
| `-32017` | Filtered account stale — simulation touches an account in the filter set; faithful replay isn't possible. |
| `-32018` | Slot in archive gap — the resolved load slot lands inside a known missing range. Pass `tolerateGaps: true` to bypass. |

The `-32014` / `-32015` split lets you route "too new — go to live RPC" and "too old — outside the archive window" to different UX. `-32016` is split from both so callers can distinguish "signature not indexed" from "out of archive range".

## Need help?

For questions about Rewind, custom filter-set requests, or wider archive windows for your workload, see the [Support](../support.md) section or contact our team.
