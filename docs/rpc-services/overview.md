# RPC Services Overview

Solana Vibe Station provides high-performance RPC endpoints with multiple service tiers to meet the needs of developers at every scale. Whether you're building a simple dApp, running high-frequency trading operations, or managing a production validator network, SVS has a tier optimized for your use case.

## Why Choose SVS?

- **On-Premise Infrastructure**: All services run on dedicated hardware in Atlanta, GA with low latency and high reliability
- **Multiple Performance Tiers**: Choose the tier that matches your application's needs and budget
- **Staked RPC Support**: Access Solana's SWQoS (Stake-Weighted QoS) for priority processing during congestion
- **Lightspeed Transactions**: Partner with our validator pool to ensure faster transaction inclusion
- **Historical Data**: Fast access to historical blockchain data without cloud dependencies

## RPC Tier Comparison

| Tier | Typical Use Case | Performance Level | Status |
|------|------------------|-------------------|--------|
| **Public** | Learning, testing, prototyping | Shared capacity | Available |
| **Lite** | Low-traffic applications, hobby projects | Basic | Available |
| **Basic** | Small production apps, moderate traffic | Standard | Available |
| **Ultra** | High-traffic dApps, frequent API calls | High | Available |
| **Elite** | Enterprise applications, mission-critical services | Very High | Available |
| **Epic** | Maximum performance requirements, institutional grade | Maximum | Available |

Performance metrics, rate limits, and RPS (requests per second) specifications are available on the [Endpoints](./endpoints.md) page.

## Endpoint URLs

All RPC endpoints follow a consistent URL pattern:

```
https://{tier}.rpc.solanavibestation.com
```

Replace `{tier}` with one of: `public`, `lite`, `basic`, `ultra`, `elite`, or `epic`.

Example endpoints:
- https://public.rpc.solanavibestation.com
- https://basic.rpc.solanavibestation.com
- https://elite.rpc.solanavibestation.com

## Staked RPC (SWQoS)

For higher tiers, SVS offers Staked RPC endpoints with Solana's Stake-Weighted Quality of Service. These endpoints reserve 80% of QUIC connections for staked nodes, ensuring priority processing during periods of network congestion.

Available staked endpoints:
- `https://basic.swqos.rpc.solanavibestation.com`
- `https://ultra.swqos.rpc.solanavibestation.com`
- `https://elite.swqos.rpc.solanavibestation.com`

Learn more in the [Staked RPC (SWQoS)](./staked-rpc.md) guide.

## Authentication

All tiers support optional authentication via:

- **Header**: `Authorization: key`
- **Query Parameter**: `?api_key=key`

Authentication is optional for public endpoints but recommended for production use to enable request tracking and higher rate limits.

## Getting Started

1. Choose the appropriate tier for your use case
2. Construct your endpoint URL
3. Make RPC calls using the standard [Solana JSON-RPC API](https://solana.com/docs/rpc/)

### Example Request

```bash
curl -X POST https://basic.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getSlot","params":[]}'
```

## Upgrade or Change Tiers

Ready to upgrade to a higher tier? Visit the [SVS Cloud Console](https://cloud.solanavibestation.com) to manage your subscription and select the tier that best fits your growing needs.

## Need Help?

For questions about choosing the right tier, API limits, or technical support, please refer to the [Support](../support.md) section or contact our team.
