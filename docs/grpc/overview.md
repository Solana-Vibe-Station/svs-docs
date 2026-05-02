# Geyser gRPC Streaming

## Overview

Geyser gRPC Streaming provides ultra-fast, real-time data transmission for Solana RPC clients through our Yellowstone Dragon's Mouth gRPC geyser plugin. This is the optimal solution for applications requiring instant access to blockchain events with minimal latency.

## What is gRPC Streaming?

gRPC is a high-performance RPC framework that enables efficient, bidirectional streaming communication. For Solana, this means you can subscribe to live events happening on-chain and receive updates with minimal delay.

### Supported Event Types

Subscribe to real-time updates for:
- **Account changes** - Monitor token balances, program state, or any account modifications
- **Transaction signatures** - Track newly confirmed transactions
- **Block notifications** - Receive updates when new blocks are produced
- **Slot updates** - Monitor validator slot production and confirmation status

## Key Features

- **Ultra-Low Latency** - Direct connection to our Atlanta datacenter infrastructure
- **Flexible Subscriptions** - Multiple subscriptions on a single connection with custom filters
- **Concurrent Stream Support** - Tiers differentiated by the number of concurrent gRPC streams
- **Simple Authentication** - IP whitelist-based access (no API keys required)
- **Program Filtering** - Subscribe only to events relevant to your Solana programs

## Authentication

Authentication for Geyser gRPC is handled via **IP whitelist**:
- No API keys needed
- No X-token required
- Simply whitelist your server's IP address during setup
- Contact support to manage your whitelist

## Service Tiers

Geyser gRPC access is available in multiple tiers based on the number of concurrent streams you need:

| Tier | Concurrent Streams | Use Case |
|------|-------------------|----------|
| Starter | 5 | Development and testing |
| Pro | 25 | Small-scale production |
| Enterprise | 100+ | Large-scale applications |

Custom tiers available for specialized use cases.

## Getting Started

To begin using Geyser gRPC:

1. **Purchase access** through our [Discord community](https://discord.gg/solanavibestation) or [Cloud platform](https://cloud.solanavibestation.com)
2. **Configure your IP whitelist** in the cloud control panel
3. **Connect to the gRPC endpoint** using your preferred client library
4. **Subscribe to events** with custom filters and parameters

## Basic Connection Example

Here's a minimal example using the `solana-grpc-client` library:

```python
import grpc
from solana_grpc import geyser_pb2, geyser_pb2_grpc

# Create channel to SVS gRPC endpoint
channel = grpc.secure_channel('grpc.solanavibestation.com:443', grpc.ssl_channel_credentials())
stub = geyser_pb2_grpc.GeyserStub(channel)

# Create a subscription for account changes
subscription_request = geyser_pb2.SubscribeRequest(
    accounts=geyser_pb2.SubscribeRequestFilterAccounts(
        account=[b'YOUR_PROGRAM_ID']
    )
)

# Stream events
for update in stub.Subscribe(subscription_request):
    print(f"Account update: {update}")
```

## What's Next?

- [Streaming Setup Guide](./streaming-setup.md) - Complete setup instructions
- [Supported Event Types](./event-types.md) - Detailed event documentation
- [Best Practices](./best-practices.md) - Optimize your subscriptions

## Support

For questions or issues, reach out to our community:
- **Discord** - Real-time support and community discussion
- **Cloud Platform Support Tickets** - Submit technical issues
