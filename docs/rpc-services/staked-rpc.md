# Staked RPC (SWQoS)

Staked RPC endpoints leverage Solana's Stake-Weighted Quality of Service (SWQoS) feature to provide priority transaction processing during periods of high network congestion.

## What is SWQoS?

Stake-Weighted Quality of Service (SWQoS) is a Solana protocol feature introduced in March 2024 that reserves 80% of QUIC connections for staked nodes. This mechanism allows validators and applications with significant stake to bypass congestion and receive priority processing.

By routing traffic through SVS's staked RPC endpoints, your transactions gain access to these reserved connection slots, dramatically improving inclusion times during peak network periods.

## SVS Staked Endpoints

Solana Vibe Station offers SWQoS endpoints for higher-tier service plans:

| Tier | SWQoS Endpoint |
|------|----------------|
| **Basic** | `https://basic.swqos.rpc.solanavibestation.com` |
| **Ultra** | `https://ultra.swqos.rpc.solanavibestation.com` |
| **Elite** | `https://elite.swqos.rpc.solanavibestation.com` |

## When to Use Staked RPC

Use staked RPC endpoints when:

- **Network congestion is high**: During periods of heavy transaction volume, staked endpoints significantly reduce wait times
- **Transaction-heavy applications**: If your dApp submits a large volume of transactions, priority processing compounds the benefits
- **MEV-sensitive operations**: Front-running risk is reduced when your transactions are prioritized through staked connections
- **Time-critical transactions**: Arbitrage, liquidation, or other latency-sensitive strategies benefit from priority inclusion
- **High-frequency trading**: Professional trading bots require predictable transaction inclusion times

For applications with moderate or unpredictable traffic, standard endpoints may be sufficient and more cost-effective.

## How It Works with SVS Infrastructure

SVS's on-premise infrastructure in Atlanta, GA is deeply integrated with Solana's validator network. When you route transactions through a SWQoS endpoint:

1. **Connection Priority**: Your connection is prioritized for one of the 80% of QUIC slots reserved for staked validators
2. **Fast Processing**: Transactions are forwarded through our validator pool with minimal latency
3. **Reduced Queueing**: Unlike standard endpoints, you avoid the congestion queues that form on public QUIC connections
4. **Reliable Inclusion**: During congestion periods, staked RPC transactions have significantly higher inclusion rates

## Example Usage

Staked RPC endpoints use the same Solana JSON-RPC API as standard endpoints. Simply change your endpoint URL:

```bash
# Standard endpoint
curl -X POST https://basic.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "sendTransaction",
    "params": ["YOUR_SIGNED_TX"]
  }'

# Staked RPC endpoint (SWQoS)
curl -X POST https://basic.swqos.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "sendTransaction",
    "params": ["YOUR_SIGNED_TX"]
  }'
```

## Performance Characteristics

During high network congestion:

- **Standard endpoints**: Transactions may experience 5-30 second delays or higher
- **Staked RPC**: Transactions typically confirm within 1-3 slots (400-1200ms)

Performance during low congestion periods is comparable between standard and staked endpoints. Reserve staked RPC for periods when network congestion is actively impacting your application.

## Pricing

Staked RPC endpoints are available on Basic, Ultra, and Elite tier subscriptions. Pricing is bundled with the tier cost. For current pricing and to upgrade, visit the [SVS Cloud Console](https://cloud.solanavibestation.com).

## API Methods

Staked RPC endpoints support all standard Solana RPC methods. Refer to the [HTTP Methods](./http-methods.md) and [WebSocket Methods](./websocket-methods.md) documentation for complete method lists.

## Best Practices

- Use staked RPC only when congestion is active; standard endpoints are sufficient and more economical during low-traffic periods
- Combine staked RPC with [Lightspeed Transactions](./lightspeed.md) for maximum inclusion priority
- Monitor network congestion via `getRecentBlockhash` or transaction confirmation times to determine when to failover to staked endpoints
- Test failover logic with both standard and staked endpoints to ensure your application handles both gracefully

## Limitations

- Not available on Public, Lite tiers
- Staked RPC provides connection priority, not guaranteed inclusion (no blockchain can guarantee that)
- SWQoS is effective during congestion; benefits are minimal during low-traffic periods
- Requires application-level awareness to switch between standard and staked endpoints

## Need More Information?

For detailed information about Solana's SWQoS feature, visit the [Solana documentation](https://solana.com/docs/core/fees#stake-weighted-quality-of-service). For questions about SVS staked RPC, refer to [Support](../support.md).
