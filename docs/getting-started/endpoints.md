# Endpoints Reference

This is the canonical reference for all Solana Vibe Station endpoints. All other documentation links here.

## HTTP RPC Endpoints

Standard Solana JSON-RPC interface over HTTP. Use these for request-response style calls.

| Tier | Endpoint |
|------|----------|
| **Public** | `https://public.rpc.solanavibestation.com` |
| **Lite** | `https://lite.rpc.solanavibestation.com` |
| **Basic** | `https://basic.rpc.solanavibestation.com` |
| **Ultra** | `https://ultra.rpc.solanavibestation.com` |
| **Elite** | `https://elite.rpc.solanavibestation.com` |
| **Epic** | `https://epic.rpc.solanavibestation.com` |

All endpoints require the standard Solana RPC request format:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "METHOD_NAME",
  "params": []
}
```

## WebSocket Endpoints

Real-time subscriptions for account changes, transaction logs, and slot updates.

| Tier | Endpoint |
|------|----------|
| **Public** | `wss://public.rpc.solanavibestation.com` |
| **Lite** | `wss://lite.rpc.solanavibestation.com` |
| **Basic** | `wss://basic.rpc.solanavibestation.com` |
| **Ultra** | `wss://ultra.rpc.solanavibestation.com` |
| **Elite** | `wss://elite.rpc.solanavibestation.com` |
| **Epic** | `wss://epic.rpc.solanavibestation.com` |

WebSocket subscriptions use the same JSON-RPC format as HTTP, with methods like `accountSubscribe`, `logsSubscribe`, `slotSubscribe`, etc.

## Staked RPC / SWQoS Endpoints

Stake-weighted Quality of Service endpoints with reserved bandwidth and transaction priority guarantees.

| Tier | Endpoint |
|------|----------|
| **Lite SWQoS** | `https://lite-swqos.rpc.solanavibestation.com` |
| **Basic SWQoS** | `https://basic-swqos.rpc.solanavibestation.com` |
| **Ultra SWQoS** | `https://ultra-swqos.rpc.solanavibestation.com` |
| **Elite SWQoS** | `https://elite-swqos.rpc.solanavibestation.com` |
| **Epic SWQoS** | `https://epic-swqos.rpc.solanavibestation.com` |

SWQoS endpoints are WebSocket-based and provide reserved bandwidth pools. See SWQoS documentation for subscription format and priority queue behavior.

## Historical RPC Endpoint

For archival queries and historical block data, POST to the `/historical` path:

```
https://{tier}.rpc.solanavibestation.com/historical
```

Example:

```
POST https://basic.rpc.solanavibestation.com/historical
```

This endpoint supports the same RPC methods as standard endpoints, with access to historical blocks and state.

## SVS API Endpoint

Solana Vibe Station proprietary API for token data, analytics, and custom queries.

```
https://beta-api.solanavibestation.com
```

See [SVS API documentation](../services/svs-api.md) for available endpoints and query formats.

## Geyser gRPC Endpoints

Real-time account and transaction streaming via gRPC protocol.

**Server Address**: Contact support for gRPC endpoint and port configuration.

**Authentication**: IP whitelist based (no API key required).

**Protocol**: gRPC with Geyser plugin message format.

See [Geyser gRPC Streaming](../services/geyser-grpc.md) for details on schema, subscription types, and setup.

## Authentication

See [Authentication](./authentication.md) for details on:
- How to pass your API key (header or query parameter)
- Which tiers require authentication
- Where to obtain and manage API keys

## Rate Limits

Different tiers have different rate limits. See [Rate Limits](./rate-limits.md) for tier-specific information and fair use policies.
