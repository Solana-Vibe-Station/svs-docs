# Authentication

Solana Vibe Station uses a flexible authentication system. The public tier requires no authentication, while paid tiers use API keys.

## RPC Endpoints (HTTP & WebSocket)

### Public Tier

The public tier endpoints require no authentication:

```bash
curl -X POST https://public.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []}'
```

### Authenticated Tiers

For lite, basic, ultra, elite, and epic tiers, include your API key in one of two ways:

**Option 1: Authorization Header (Recommended)**

```bash
curl -X POST https://basic.rpc.solanavibestation.com \
  -H "Content-Type: application/json" \
  -H "Authorization: your-api-key" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []}'
```

**Option 2: Query Parameter**

```bash
curl -X POST 'https://basic.rpc.solanavibestation.com?api_key=your-api-key' \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []}'
```

### JavaScript Example

```javascript
const web3 = require("@solana/web3.js");

const connection = new web3.Connection(
  "https://basic.rpc.solanavibestation.com",
  "confirmed"
);

// The web3.js library doesn't directly support custom headers in the Connection object.
// For authenticated requests, use the fetch API directly:

const method = "getLatestBlockhash";
const params = [];

const response = await fetch("https://basic.rpc.solanavibestation.com", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: "your-api-key",
  },
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method,
    params,
  }),
});

const data = await response.json();
console.log("Latest blockhash:", data.result.blockhash);
```

### Python Example

```python
import requests

url = "https://basic.rpc.solanavibestation.com"
headers = {
    "Content-Type": "application/json",
    "Authorization": "your-api-key"
}
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getLatestBlockhash",
    "params": []
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()
print("Latest blockhash:", data["result"]["blockhash"])
```

## SVS API

The SVS API uses the same authentication mechanism as RPC endpoints:

**Header:**
```
Authorization: your-api-key
```

**Query Parameter:**
```
https://beta-api.solanavibestation.com/endpoint?api_key=your-api-key
```

See [SVS API documentation](../services/svs-api.md) for endpoint specifics.

## Geyser gRPC

Geyser gRPC streaming uses **IP whitelist authentication** instead of API keys. No API key header is required.

**Authentication**: Your client IP address must be whitelisted. Contact support to register your IP addresses.

**Setup**: Connect to the gRPC endpoint with your whitelisted IP. No additional authentication headers needed.

See [Geyser gRPC Streaming](../services/geyser-grpc.md) for protocol details.

## Getting and Managing Your API Key

### Obtain an API Key

1. Visit [cloud.solanavibestation.com](https://cloud.solanavibestation.com)
2. Create an account or sign in
3. Choose your tier (lite, basic, ultra, elite, epic)
4. Generate an API key in your dashboard
5. Copy the key—you'll use it for all authenticated requests

### Rotate Your Key

To rotate your API key for security:

1. Log in to [cloud.solanavibestation.com](https://cloud.solanavibestation.com)
2. Navigate to API Keys
3. Generate a new key
4. Update your application to use the new key
5. Delete the old key once you've confirmed the new one works

### Security Best Practices

- **Never commit API keys to version control**: Use environment variables or secrets management
- **Use the header approach when possible**: Headers are not logged in URL history or server logs like query parameters can be
- **Rotate regularly**: Generate new keys periodically, especially after security incidents
- **Scope to minimum tier needed**: Use the lowest tier that meets your application's needs
- **Monitor usage**: Check your dashboard for unexpected activity

## Tier-Specific Limits

Different tiers have different rate limits and quotas. See [Rate Limits](./rate-limits.md) for details.
