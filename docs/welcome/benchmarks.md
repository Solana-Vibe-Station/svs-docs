# Benchmarks & Performance

Solana Vibe Station infrastructure is colocated in a single Atlanta, GA datacenter with direct-attach networking. This unified infrastructure approach enables consistently low latency and high throughput.

## Live Metrics

We post real-time performance metrics every 5 minutes to our Discord community. Join us there to see live data on:

- **Endpoint Latency**: RPC response times by tier
- **Throughput**: Requests per second capacity
- **Uptime**: Real-time availability statistics
- **Network Performance**: Stream subscription latency

**Discord**: Check the metrics channel for current performance data.

This approach gives you visibility into real, up-to-the-minute performance rather than static benchmarks that may not reflect current conditions.

## Infrastructure Characteristics

All SVS infrastructure runs in our Atlanta datacenter:

- **Network Topology**: Direct-attach SFP+ connections, VLAN-isolated by service tier
- **No Noisy Neighbor Effects**: Dedicated hardware (not cloud-shared instances)
- **Consistent Performance**: Single colocation facility means no cross-region latency variability
- **Hardware-Optimized**: Purpose-built for Solana's transaction throughput and block processing

## Performance by Tier

Different service tiers provide different resource allocations:

| Tier | Use Case | Relative Latency | Relative Throughput |
|------|----------|-----------------|-------------------|
| **Public** | Development, read-only | Highest | Baseline |
| **Lite** | Light load applications | Good | Standard |
| **Basic** | General production | Good | Standard |
| **Ultra** | Low-latency applications | Low | High |
| **Elite** | Mission-critical, highest priority | Very Low | Very High |
| **Epic** | Maximum performance, dedicated resources | Lowest | Highest |

SWQoS variants (Staked RPC) provide additional throughput and priority guarantees based on stake-weighted allocation.

## Real-World Testing

We encourage developers to:

1. **Test Endpoints**: Connect to the tier you're considering and measure latency from your infrastructure
2. **Check Discord Metrics**: See live performance data updated every 5 minutes
3. **Start with Public**: Evaluate the platform risk-free with the public tier
4. **Monitor During Peak**: Performance metrics during high network load are the best indicator of production reliability

## What to Track

When evaluating performance for your workload, the metrics we recommend watching are:

- **Latency percentiles** — `p50`, `p95`, and `p99` response times for the RPC methods you actually use
- **Throughput** — sustained requests per second under your real traffic pattern, not synthetic bursts
- **Uptime** — availability over rolling 30/90-day windows
- **Geyser stream latency** — slot-arrival lag for subscription-based workloads

Live values across all of these are posted to the metrics channel in our Discord every 5 minutes. If you have a specific benchmark request or want infrastructure detail beyond what's posted publicly, reach out via [Contact](../support/contact.md).
