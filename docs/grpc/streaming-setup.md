# gRPC Streaming Setup Guide

## Getting Access

### Option 1: Purchase via Discord

1. Join our [Solana Vibe Station Discord community](https://discord.gg/solanavibestation)
2. Navigate to the **#marketplace** or **#sales** channel
3. Use the bot commands to purchase gRPC access
4. Select your desired tier based on concurrent stream requirements
5. Complete payment

### Option 2: Purchase via Cloud Platform

1. Visit [https://cloud.solanavibestation.com](https://cloud.solanavibestation.com)
2. Sign in or create an account
3. Navigate to **Services** > **gRPC Streaming**
4. Select your tier and complete checkout
5. Your credentials will be available immediately in the dashboard

## Configuring IP Whitelist

After purchasing gRPC access, you need to whitelist the IP addresses that will connect to the service.

### Via Cloud Dashboard

1. Log into [https://cloud.solanavibestation.com](https://cloud.solanavibestation.com)
2. Go to **gRPC** > **Settings**
3. Click **Manage IP Whitelist**
4. Add your server IP address(es)
   - Single IP: `192.0.2.1`
   - CIDR range: `192.0.2.0/24`
5. Save changes

The whitelist is updated immediately—no restart required.

### Via Discord Bot

Use our Discord bot to manage your whitelist:

```
/grpc whitelist add <your-ip-address>
/grpc whitelist remove <your-ip-address>
/grpc whitelist list
```

## Connection Details

### Endpoint

```
grpc.solanavibestation.com:443
```

### Protocol

- **TLS/SSL** - All connections must use secure TLS
- **Port** - Standard gRPC port 443
- **Protocol Version** - gRPC over HTTP/2

### Connection Configuration

```yaml
endpoint: grpc.solanavibestation.com
port: 443
tls: true
max_concurrent_streams: <based-on-your-tier>
```

## Basic Subscription Example

### Account Change Subscription

Subscribe to updates when a specific program's accounts change:

```python
import grpc
from solana_grpc import geyser_pb2, geyser_pb2_grpc

channel = grpc.secure_channel('grpc.solanavibestation.com:443',
                             grpc.ssl_channel_credentials())
stub = geyser_pb2_grpc.GeyserStub(channel)

# Subscribe to account changes for a specific program
request = geyser_pb2.SubscribeRequest(
    accounts=geyser_pb2.SubscribeRequestFilterAccounts(
        owner=[bytes.fromhex('YOUR_PROGRAM_ID')],
    )
)

for update in stub.Subscribe(request):
    print(f"Update: {update}")
    if update.HasField('account'):
        account = update.account
        print(f"Account: {account.pubkey}")
        print(f"Lamports: {account.lamports}")
```

### Transaction Subscription

Monitor all transactions on the network:

```python
request = geyser_pb2.SubscribeRequest(
    transactions=geyser_pb2.SubscribeRequestFilterTransactions(
        vote=False,
        failed=False,
    )
)

for update in stub.Subscribe(request):
    if update.HasField('transaction'):
        tx = update.transaction
        print(f"New transaction: {tx.signature}")
```

### Block Subscription

Receive updates when blocks are produced:

```python
request = geyser_pb2.SubscribeRequest(
    blocks=geyser_pb2.SubscribeRequestFilterBlocks()
)

for update in stub.Subscribe(request):
    if update.HasField('block'):
        block = update.block
        print(f"Block {block.slot} produced by {block.leader}")
```

## Supported Subscription Types

| Type | Description | Filter Support |
|------|-------------|-----------------|
| **Accounts** | Account state changes | Owner, address, tokens |
| **Transactions** | Transaction confirmations | Vote, failed, signature |
| **Blocks** | New block production | Slot range, leader |
| **Slots** | Slot updates and confirmations | Root, first shredded |
| **Entries** | Transaction entries in blocks | None |

## Managing Multiple Subscriptions

You can maintain multiple subscriptions on a single connection:

```python
# Create multiple subscription requests on the same channel
request_1 = geyser_pb2.SubscribeRequest(...)  # Account changes
request_2 = geyser_pb2.SubscribeRequest(...)  # Transactions
request_3 = geyser_pb2.SubscribeRequest(...)  # Blocks

# Each subscription can be managed independently
stream_1 = stub.Subscribe(request_1)
stream_2 = stub.Subscribe(request_2)
stream_3 = stub.Subscribe(request_3)

# Use threading or async to handle multiple streams
```

## Best Practices

### Connection Management

- Implement automatic reconnection with exponential backoff
- Monitor connection health and log disconnections
- Use connection pooling for multiple subscriptions
- Set reasonable timeout values (typically 30-60 seconds)

### Filter Optimization

- Be as specific as possible with your filters to reduce bandwidth
- Avoid subscribing to all accounts or transactions if you only need specific data
- Use owner filters for token programs to reduce noise
- Combine related subscriptions when possible

### Resource Management

- Monitor your concurrent stream count against your tier limit
- Gracefully close subscriptions when no longer needed
- Implement backpressure handling for high-volume streams
- Log unusual patterns in subscription behavior

## Troubleshooting Connection Issues

### Connection Refused

- Verify your IP is whitelisted in the cloud dashboard
- Check firewall rules allow outbound HTTPS (443)
- Ensure you're using the correct endpoint: `grpc.solanavibestation.com:443`

### Authentication Errors

- Confirm your IP whitelist is configured
- If recently added, wait a few seconds for propagation
- Check that your client IP matches whitelist (not a proxy/NAT IP)

### High Latency

- Verify you're on the latest client library version
- Check your network connection to our Atlanta datacenter
- Monitor CPU usage on your client to ensure it's not the bottleneck

## Next Steps

- Review [Event Types & Schemas](./event-types.md) for detailed data formats
- Check [Best Practices](./best-practices.md) for optimization tips
- Review [Troubleshooting](../support/troubleshooting.md) for common issues

## Support

Need help? Reach out to our community:
- **Discord** - [Join our server](https://discord.gg/solanavibestation) for real-time assistance
- **Cloud Platform Tickets** - Submit technical issues through your dashboard
