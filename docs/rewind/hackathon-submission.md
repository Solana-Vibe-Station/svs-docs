# Rewind — Hackathon Submission Copy

Three sections, each ready to drop into the submission form. Each paragraph is a single unwrapped line so copy-paste won't pick up stray newlines.

---

## Brief Description

Rewind is a historical state and simulation service for Solana. It lets you look up any account's value at any past slot, walk every write that account ever received, and re-run real transactions against the exact on-chain state they would have seen — all over plain JSON-RPC.

---

## What are you building, and who is it for?

Rewind is a JSON-RPC service that does three things standard Solana RPC can't:

1. **Point-in-time account reads.** Ask for a pubkey's state at slot `N`, or "the moment immediately before transaction `<sig>` ran," and get back the account exactly as it was — same lamports, same data, same owner, same rent epoch. The wire format matches Solana's `getAccountInfo` so existing SDKs work unchanged.
2. **Per-write change history.** Walk every mutation an account has received over a slot range, newest first, with the producing transaction signature attached. Pagination is cursor-based and stable.
3. **Historical transaction replay.** Submit any signed `VersionedTransaction` and Rewind runs it through the SVM against archive state — with the right feature set, sysvars, address-lookup tables, and program bytecode for the slot you pin to. Same response shape as `simulateTransaction`, except now you can ask "what would this have done at 3 a.m. last Tuesday?"

On top of those three primitives we built an async job framework: **sweep jobs** that run a transaction at every Nth slot across a range, **trigger jobs** that find every moment a predicate held and simulate the tx there, and **discovery jobs** that match parameterized strategy templates against history to surface every opportunity that existed. Submit, poll, paginate.

**Who it's for.** Anyone whose product needs a Solana time machine:

- **Arbitrage and market-making teams** that want to backtest a strategy against the real on-chain state of every block, not a synthetic approximation.
- **MEV researchers** doing post-mortems on landed and missed opportunities — replay the exact bundle, see what the runtime saw.
- **DeFi protocols** investigating user-reported bugs ("my swap reverted yesterday") by replaying the failing transaction at the exact slot it ran.
- **Analytics platforms** that need per-write account history for indexing, dashboards, or compliance audits.
- **Security researchers and auditors** validating that a fix would have prevented an exploit by replaying the exploit transaction against the patched state.

Rewind hides the index, the storage, and the simulator behind a single JSON-RPC endpoint. If you can hit `getAccountInfo` today, you can hit Rewind tomorrow.

---

## Why did you decide to build this — and why now?

Three things came together.

**The questions that mattered most weren't being answered.** The Solana RPC interface is excellent for "what's happening right now" and OK for "what happened in this specific block," but it falls off a cliff for "what was true at this exact moment in the past." Building a real backtester, replaying a failed transaction with confidence, or running a strategy template across last week's history means stitching together your own archive — and most teams either give up or pay a specialized provider an enterprise rate. We wanted those questions to be a single JSON-RPC call.

**Solana's history is finally rich enough to be worth replaying.** Mainnet has years of behavior in the archive now: real swaps, real liquidations, real exploits, real congestion patterns. Without historical simulation, all of that is read-only — you can see *what happened* but you can't ask *what would have happened*. As DeFi and MEV ecosystems mature, the value of being able to test your code against real history (not a unit-test mock) keeps growing.

**Standing on the shoulders of LiteSVM and modern indexing.** The combination of Yellowstone gRPC giving us per-write account streams, LiteSVM letting us spin up a full-fidelity SVM in milliseconds, and column-store backends that handle billions of writes makes a service like this buildable today in a way that wouldn't have worked even a year or two ago. The pieces exist; somebody had to glue them together with the right developer ergonomics on top.

So we built Rewind to be the one boring, JSON-RPC-shaped layer on the front: ask a question about the past, get an answer. No batch jobs to spin up, no infrastructure to run, no proprietary client. Same wire format you already know, pointed at the slot you actually care about.
