# Rate Limits & Fair Use

Solana Vibe Station implements rate limiting to ensure fair resource allocation and reliable service for all users.

## RPC Endpoint Rate Limits

Rate limits vary by tier. Your tier determines how many requests per second you can make:

| Tier | Requests/Second | Typical Use Case |
|------|-----------------|-----------------|
| **Public** | Shared | Development, testing, low-volume reads |
| **Lite** | 10 req/s | Light production applications |
| **Basic** | 50 req/s | General production workloads |
| **Ultra** | 200 req/s | High-frequency trading, arbitrage bots |
| **Elite** | 500 req/s | Mission-critical, enterprise applications |
| **Epic** | Unlimited* | Dedicated infrastructure, custom SLA |

*Epic tier includes dedicated resources. Contact sales for specifics.

## SVS API Rate Limits

The SVS API (beta) is currently free and has the following limits:

- **Rate**: 25 requests/second per IP address
- **Batch Size**: Maximum 36 items per request
- **Timeout**: 30 second request timeout

These limits apply globally across all users on the public SVS API. Respect these limits to avoid temporary IP-based rate limiting.

## WebSocket Subscriptions

WebSocket connections have per-connection limits:

- **Public Tier**: 10 concurrent subscriptions
- **Lite Tier**: 25 concurrent subscriptions
- **Basic Tier**: 50 concurrent subscriptions
- **Ultra Tier**: 100 concurrent subscriptions
- **Elite Tier**: 250 concurrent subscriptions
- **Epic Tier**: Unlimited

## Rate Limit Responses

When you exceed your rate limit, you'll receive an HTTP 429 (Too Many Requests) response:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Rate limit exceeded",
    "data": {
      "retry_after": 60
    }
  },
  "id": 1
}
```

The `retry_after` field indicates seconds to wait before retrying.

## Responsible Usage

To avoid rate limiting and ensure service quality for everyone:

### Batch Requests When Possible

Instead of making individual calls, batch multiple operations:

```bash
# Good: Batch call
curl -X POST https://basic.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getMultipleAccounts",
    "params": [
      ["account1", "account2", "account3"],
      {"encoding": "jsonParsed"}
    ]
  }'
```

### Cache When Possible

Avoid repeated calls for data that doesn't change frequently:

```javascript
// Cache blockhash for 30 seconds
let cachedBlockhash = null;
let blockHashExpiry = null;

async function getBlockhash(connection) {
  const now = Date.now();
  if (cachedBlockhash && blockHashExpiry > now) {
    return cachedBlockhash;
  }

  const { blockhash } = await connection.getLatestBlockhash();
  cachedBlockhash = blockhash;
  blockHashExpiry = now + 30000; // 30 second cache
  return blockhash;
}
```

### Use WebSocket for Real-Time Data

Instead of polling with repeated HTTP requests, use WebSocket subscriptions:

```javascript
// Bad: Polling every 100ms
setInterval(async () => {
  const balance = await connection.getBalance(publicKey);
  console.log(balance);
}, 100);

// Good: WebSocket subscription
connection.onAccountChange(publicKey, (accountInfo) => {
  const lamports = accountInfo.lamports;
  console.log(lamports);
});
```

### Implement Backoff

If you hit rate limits, implement exponential backoff:

```javascript
async function requestWithBackoff(fn, maxRetries = 5) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429) {
        const delay = Math.pow(2, i) * 1000; // Exponential backoff
        console.log(`Rate limited. Waiting ${delay}ms before retry...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
  throw new Error("Max retries exceeded");
}

// Usage
const balance = await requestWithBackoff(() =>
  connection.getBalance(publicKey)
);
```

### Upgrade Your Tier

If your application consistently needs more throughput, upgrading your tier gives you:
- Higher rate limits
- Lower latency
- Priority resource allocation
- Dedicated support

Visit [cloud.solanavibestation.com](https://cloud.solanavibestation.com) to upgrade.

## Geyser gRPC Rate Limits

Geyser gRPC streams do not have per-request rate limits. Instead, you're limited by the per-connection subscription limits (see WebSocket Subscriptions above). A single gRPC connection can maintain multiple subscriptions up to your tier's limit.

## Questions?

For questions about rate limits or to discuss custom arrangements for enterprise use cases, contact support via Discord or [cloud.solanavibestation.com](https://cloud.solanavibestation.com).
